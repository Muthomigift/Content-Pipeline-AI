
import os
import logging

from flask import Flask, request, render_template_string
from dotenv import load_dotenv

from pipeline import generate_content_package, ContentPipelineError


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


# Configure logging
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger(__name__)


# Frontend
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Content Pipeline AI</title>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #f8fafc;
            color: #1e293b;
            min-height: 100vh;
        }

        .navbar {
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 20px 7%;
        }

        .logo {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.7px;
        }

        .logo span {
            color: #6d5ce7;
        }

        .container {
            max-width: 850px;
            margin: 65px auto;
            padding: 0 22px;
        }

        .hero {
            text-align: center;
            margin-bottom: 38px;
        }

        .hero h1 {
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -1.5px;
            margin-bottom: 13px;
            color: #172033;
        }

        .hero p {
            color: #64748b;
            font-size: 15px;
            line-height: 1.7;
        }

        .generator {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.035);
        }

        .generator h2 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .description {
            color: #64748b;
            font-size: 13px;
            margin-bottom: 22px;
            line-height: 1.6;
        }

        textarea {
            width: 100%;
            min-height: 145px;
            padding: 16px;
            border: 1px solid #dbe1e8;
            border-radius: 8px;
            font-family: inherit;
            font-size: 14px;
            line-height: 1.6;
            color: #1e293b;
            background: #ffffff;
            resize: vertical;
            outline: none;
        }

        textarea:focus {
            border-color: #8b7cf6;
            box-shadow: 0 0 0 3px rgba(139, 124, 246, 0.10);
        }

        textarea::placeholder {
            color: #94a3b8;
        }

        .generate-btn {
            width: 100%;
            margin-top: 16px;
            padding: 14px;
            background: #6d5ce7;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-family: inherit;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .generate-btn:hover {
            background: #5948d5;
        }

        .generate-btn:disabled {
            opacity: 0.65;
            cursor: wait;
        }

        .error {
            margin-top: 22px;
            padding: 14px 16px;
            background: #fff1f2;
            border: 1px solid #fecdd3;
            border-radius: 8px;
            color: #be123c;
            font-size: 13px;
            line-height: 1.6;
        }

        .results-heading {
            margin: 45px 0 20px;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .result-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 18px;
        }

        .result-card h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 18px;
            color: #334155;
        }

        .blog-title {
            font-size: 21px;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 15px;
            color: #172033;
        }

        .result-content {
            color: #475569;
            font-size: 14px;
            line-height: 1.9;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            margin-bottom: 18px;
        }

        .tweet {
            padding: 18px 0;
            border-top: 1px solid #edf0f4;
        }

        .tweet:first-of-type {
            border-top: none;
        }

        .tweet p {
            font-size: 14px;
            color: #475569;
            line-height: 1.8;
            margin-bottom: 12px;
            overflow-wrap: anywhere;
        }

        .copy-btn {
            padding: 8px 13px;
            background: #f5f3ff;
            color: #6d5ce7;
            border: 1px solid #e5e0ff;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }

        .copy-btn:hover {
            background: #ede9fe;
        }

        .footer {
            text-align: center;
            padding: 30px 15px;
            color: #94a3b8;
            font-size: 12px;
            border-top: 1px solid #e5e7eb;
            margin-top: 60px;
            background: #ffffff;
        }

        @media (max-width: 600px) {
            .navbar {
                padding: 18px 22px;
            }

            .container {
                margin: 45px auto;
            }

            .hero h1 {
                font-size: 29px;
            }

            .generator,
            .result-card {
                padding: 20px;
            }
        }
    </style>
</head>

<body>

    <nav class="navbar">
        <div class="logo">Content<span>Pipeline</span> AI</div>
    </nav>

    <main class="container">

        <section class="hero">
            <h1>Turn one idea into multiple contents.</h1>

            <p>
                Generate a blog post, five X posts, and a LinkedIn post
                from a single topic or article.
            </p>
        </section>

        <section class="generator">

            <h2>Content generator</h2>

            <p class="description">
                Enter a topic or paste an article URL below.
            </p>

            <form method="POST" id="contentForm">

                <textarea
                    name="topic"
                    placeholder="What would you like to create content about?"
                    required
                >{{ topic or '' }}</textarea>

                <button
                    type="submit"
                    class="generate-btn"
                    id="generateBtn"
                >
                    Generate content
                </button>

            </form>

        </section>

        {% if error %}
            <div class="error">
                {{ error }}
            </div>
        {% endif %}

        {% if package %}

            <h2 class="results-heading">Generated content</h2>

            <section class="result-card">

                <h3>Blog post</h3>

                <div class="blog-title">
                    {{ package.blog_post.title }}
                </div>

                <div class="result-content" id="blogContent">{{ package.blog_post.content }}</div>

                <button class="copy-btn" onclick="copyContent('blogContent', this)">
                    Copy blog post
                </button>

            </section>

            <section class="result-card">

                <h3>Five X posts</h3>

                {% for tweet in package.tweets %}

                    <div class="tweet">

                        <p id="tweet{{ loop.index }}">{{ tweet }}</p>

                        <button
                            class="copy-btn"
                            onclick="copyContent('tweet{{ loop.index }}', this)"
                        >
                            Copy post
                        </button>

                    </div>

                {% endfor %}

            </section>

            <section class="result-card">

                <h3>LinkedIn post</h3>

                <div class="result-content" id="linkedinContent">{{ package.linkedin_post }}</div>

                <button class="copy-btn" onclick="copyContent('linkedinContent', this)">
                    Copy LinkedIn post
                </button>

            </section>

        {% endif %}

    </main>

    <footer class="footer">
        Content Pipeline AI · Powered by Anthropic Claude
    </footer>

    <script>

        const form = document.getElementById("contentForm");
        const button = document.getElementById("generateBtn");

        form.addEventListener("submit", function () {
            button.disabled = true;
            button.textContent = "Generating content...";
        });

        async function copyContent(elementId, button) {

            const element = document.getElementById(elementId);
            const text = element.innerText;

            try {

                await navigator.clipboard.writeText(text);

                const originalText = button.textContent;

                button.textContent = "Copied!";

                setTimeout(() => {
                    button.textContent = originalText;
                }, 1500);

            } catch (error) {

                button.textContent = "Copy failed";

            }
        }

    </script>

</body>
</html>
"""


# Main application route
@app.route("/", methods=["GET", "POST"])
def home():

    package = None
    error = None
    topic = ""

    if request.method == "POST":

        topic = request.form.get("topic", "").strip()

        logger.info("New content generation request received.")

        try:

            logger.info("Processing user topic.")

            package = generate_content_package(topic)

            logger.info("Content generated successfully.")

        except ContentPipelineError as exc:

            error = str(exc)

            logger.warning(
                "Content generation failed: %s",
                error
            )

        except Exception:

            logger.exception("Unexpected application error.")

            error = (
                "Something went wrong while generating your content. "
                "Please try again."
            )

    return render_template_string(
        HTML_PAGE,
        package=package,
        error=error,
        topic=topic
    )


@app.errorhandler(413)
def request_too_large(error):
    return "Your request is too large. Please shorten your input.", 413


@app.errorhandler(404)
def page_not_found(error):
    return "Page not found.", 404


@app.errorhandler(500)
def internal_server_error(error):
    logger.exception("Internal server error.")
    return "An internal server error occurred.", 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
