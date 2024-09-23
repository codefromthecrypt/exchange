import os
import pytest

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_API_KEY = "test_openai_api_key"
OPENAI_ORG_ID = "test_openai_org_key"
OPENAI_PROJECT_ID = "test_openai_project_id"


@pytest.fixture
def default_openai_api_key(monkeypatch):
    """
    This fixture avoids the error OpenAiProvider.from_env() raises when the
    OPENAI_API_KEY is not set in the environment.

    When running VCR tests for the first time or after deleting a cassette
    recording, a real OPENAI_API_KEY must be passed as an environment variable,
    so real responses can be fetched. Subsequent runs use the recorded data, so
    don't need a real key.
    """
    if "OPENAI_API_KEY" not in os.environ:
        monkeypatch.setenv("OPENAI_API_KEY", OPENAI_API_KEY)


@pytest.fixture(scope="module")
def vcr_config():
    """
    This scrubs sensitive data and gunzips bodies when in recording mode.

    Without this, you would leak cookies and auth tokens in the cassettes.
    Also, depending on the request, some responses would be binary encoded
    while others plain json. This ensures all bodies are human-readable.
    """
    return {
        "decode_compressed_response": True,
        "filter_headers": [
            ("authorization", "Bearer " + OPENAI_API_KEY),
            ("openai-organization", OPENAI_ORG_ID),
            ("openai-project", OPENAI_PROJECT_ID),
            ("cookie", None),
        ],
        "before_record_response": scrub_response_headers,
    }


def scrub_response_headers(response):
    """
    This scrubs sensitive response headers. Note they are case-sensitive!
    """
    response["headers"]["openai-organization"] = OPENAI_ORG_ID
    response["headers"]["Set-Cookie"] = "test_set_cookie"
    return response