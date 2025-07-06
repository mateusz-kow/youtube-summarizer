# tests/test_llm.py
import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from ytsum.llms.gemini import Gemini


# Setup Gemini with a mock client
@pytest.fixture
def mock_gemini_client() -> Generator[MagicMock, None, None]:
    """Fixture to mock the genai.Client."""
    with patch("google.genai.Client") as mock_client_constructor:
        mock_client = MagicMock()
        mock_client_constructor.return_value = mock_client
        # Set environment variables for the test
        os.environ["GOOGLE_API_KEY"] = "test-key"
        os.environ["GOOGLE_MODEL_NAME"] = "test-model"
        os.environ["GOOGLE_LLM_MAX_INPUT_TOKENS"] = "100"
        yield mock_client


def test_gemini_ask_success(mock_gemini_client: MagicMock) -> None:
    """Tests a successful API call to Gemini."""
    # Arrange
    llm = Gemini()
    mock_response = MagicMock()
    mock_response.text = "This is a summary. "
    mock_gemini_client.models.generate_content.return_value = mock_response

    # Act
    result = llm.ask("Test prompt")

    # Assert
    assert result == "This is a summary."
    mock_gemini_client.models.generate_content.assert_called_once()
