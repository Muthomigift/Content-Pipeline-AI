import pytest

from pipeline import (
    validate_topic,
    validate_url,
    ContentPipelineError
)


def test_valid_topic():
    validate_topic("Artificial intelligence in business")


def test_empty_topic():
    with pytest.raises(ContentPipelineError):
        validate_topic("")


def test_topic_too_short():
    with pytest.raises(ContentPipelineError):
        validate_topic("AI")


def test_valid_url():
    validate_url("https://example.com")


def test_invalid_url():
    with pytest.raises(ContentPipelineError):
        validate_url("not-a-valid-url")