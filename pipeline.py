import os
import json
import logging
import ipaddress
import socket
from urllib.parse import urlparse

import anthropic
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class ContentPipelineError(Exception):
    """Custom exception for content generation errors."""
    pass


def validate_topic(topic):
    """Validate the user's topic."""

    if not topic or not topic.strip():
        raise ContentPipelineError("Please enter a topic or URL.")

    if len(topic.strip()) < 5:
        raise ContentPipelineError("Your topic is too short.")

    return topic.strip()


def validate_url(url):
    """Validate URLs and block private network addresses."""

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ContentPipelineError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname:
        raise ContentPipelineError("Invalid URL provided.")

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname, None
        )

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ContentPipelineError(
                    "Private or restricted URLs are not allowed."
                )

    except ContentPipelineError:
        raise

    except socket.gaierror:
        raise ContentPipelineError("Unable to locate the website.")

    return url


def extract_url_content(url):
    """Extract readable text from a webpage."""

    validate_url(url)

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 ContentPipelineBot/1.0"
            },
            allow_redirects=False
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            raise ContentPipelineError(
                "The URL must point to an HTML webpage."
            )

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if len(text) < 100:
            raise ContentPipelineError(
                "Not enough readable content found on this webpage."
            )

        return text[:12000]

    except requests.RequestException as error:
        logger.exception("Website extraction failed.")

        raise ContentPipelineError(
            "Could not access the webpage. Check the URL and try again."
        ) from error


def generate_content_package(topic):
    """
    Generate a blog post, five tweets and one LinkedIn post.
    Accepts either a topic or an article URL.
    """

    topic = validate_topic(topic)

    if topic.startswith(("http://", "https://")):
        logger.info("Processing article URL.")

        source_content = extract_url_content(topic)

        content_source = f"""
        Create content based on this webpage:

        Source URL: {topic}

        Article content:
        {source_content}
        """

    else:
        logger.info("Processing user topic.")

        content_source = f"""
        Create content based on this topic:

        {topic}
        """

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv(
        "ANTHROPIC_MODEL",
        "claude-sonnet-4-5"
    )

    if not api_key:
        raise ContentPipelineError(
            "Anthropic API key is missing. Configure your environment."
        )

    prompt = f"""
    You are an expert digital marketing content strategist.

    Create a complete content package for a business audience.

    {content_source}

    Generate the following:

    1. BLOG POST:
       - An engaging title.
       - A strong introduction.
       - Clear headings and sections.
       - Useful, informative content.
       - A conclusion.
       - A call to action.

    2. FIVE TWEETS:
       - Generate exactly five tweets.
       - Make each engaging and easy to understand.
       - Each should work as an independent social media post.
       - Avoid unnecessary repetition.

    3. LINKEDIN POST:
       - Professional and engaging.
       - Suitable for a business audience.
       - Include a strong opening and call to action.

    Return ONLY valid JSON using this exact structure:

    {{
        "blog_post": {{
            "title": "Blog title",
            "content": "Complete blog post in Markdown"
        }},
        "tweets": [
            "Tweet 1",
            "Tweet 2",
            "Tweet 3",
            "Tweet 4",
            "Tweet 5"
        ],
        "linkedin_post": "Complete LinkedIn post"
    }}

    Do not include Markdown code fences around the JSON.
    Do not invent statistics, facts or sources.
    """

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text

        package = json.loads(response_text)

        # Validate the generated response
        if not isinstance(package, dict):
            raise ValueError("Invalid response structure.")

        blog = package.get("blog_post")
        tweets = package.get("tweets")
        linkedin = package.get("linkedin_post")

        if not isinstance(blog, dict):
            raise ValueError("Blog post is missing.")

        if not blog.get("title") or not blog.get("content"):
            raise ValueError("Blog post is incomplete.")

        if not isinstance(tweets, list) or len(tweets) != 5:
            raise ValueError("Exactly five tweets are required.")

        if not all(
            isinstance(tweet, str) and tweet.strip()
            for tweet in tweets
        ):
            raise ValueError("One or more tweets are empty.")

        if not isinstance(linkedin, str) or not linkedin.strip():
            raise ValueError("LinkedIn post is missing.")

        logger.info("Content package generated successfully.")

        return package

    except anthropic.AuthenticationError as error:
        logger.exception("Anthropic authentication failed.")

        raise ContentPipelineError(
            "Invalid Anthropic API key. Check your configuration."
        ) from error

    except anthropic.RateLimitError as error:
        logger.exception("Anthropic rate limit reached.")

        raise ContentPipelineError(
            "The AI service is currently busy. Please try again later."
        ) from error

    except anthropic.APIConnectionError as error:
        logger.exception("Could not connect to Anthropic.")

        raise ContentPipelineError(
            "Unable to connect to the AI service. Try again later."
        ) from error

    except anthropic.APIStatusError as error:
        logger.exception("Anthropic API returned an error.")

        raise ContentPipelineError(
            "The AI service returned an error. Please try again."
        ) from error

    except (json.JSONDecodeError, ValueError, IndexError, AttributeError) as error:
        logger.exception("Invalid AI response.")

        raise ContentPipelineError(
            "The AI returned an invalid response. Please try again."
        ) from error
