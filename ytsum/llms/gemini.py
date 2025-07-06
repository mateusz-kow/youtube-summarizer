import logging
import os
import time

from google import genai
from google.genai.errors import ClientError

from ytsum.llms.llm import LLM

logger = logging.getLogger(__name__)


class Gemini(LLM):
    """
    Implementation of the LLM interface using Google Gemini language model.

    This class manages interactions with the Gemini API including
    token counting, request retries on quota exhaustion, and response handling.
    """

    def __init__(
        self, max_tokens: int = int(os.getenv("GOOGLE_LLM_MAX_INPUT_TOKENS", 6000))
    ):
        """
        Initialize Gemini LLM client with max token limit and model configuration.

        Args:
            max_tokens (int, optional): Maximum tokens allowed per prompt. Defaults to 6000 or environment variable.
        """
        super().__init__(logger)
        self._max_tokens = max_tokens
        self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self._model_name = os.getenv("GOOGLE_MODEL_NAME", "gemma-3n-e4b-it")
        logger.info(f"Gemini initialized with max token limit: {self._max_tokens}")

    def ask(self, prompt: str, max_retries: int = 5, backoff_seconds: int = 30) -> str:
        """
        Send prompt to Gemini model and retrieve response with retry on quota errors.

        Args:
            prompt (str): The input prompt string.
            max_retries (int, optional): Maximum retry attempts on quota exhaustion. Defaults to 5.
            backoff_seconds (int, optional): Wait time between retries in seconds. Defaults to 30.

        Raises:
            RuntimeError: If all retry attempts fail due to quota exhaustion.
            Exception: On unexpected API errors.

        Returns:
            str: The model's response text.
        """
        tokens = self.get_token_count(prompt)
        logger.debug(f"Calling Gemini with prompt: {prompt} and tokens {tokens}")

        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name, contents=prompt
                )
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini model.")
                return response.text.strip()
            except ClientError as e:
                error_msg = str(e)
                if "RESOURCE_EXHAUSTED" in error_msg:
                    logger.warning(
                        f"Quota exceeded (attempt {attempt}/{max_retries}). "
                        f"Retrying in {backoff_seconds} seconds..."
                    )
                    time.sleep(backoff_seconds)
                else:
                    logger.error(f"Unexpected API error: {e}")
                    raise

        raise RuntimeError(
            "Failed to get response after multiple retries due to quota exhaustion."
        )

    def get_token_count(self, text: str) -> int:
        """
        Return the number of tokens in the input text, using Gemini token counting API.

        Falls back to a heuristic estimate if the API call fails.

        Args:
            text (str): Input text to count tokens for.

        Returns:
            int: Number of tokens counted or estimated.
        """
        if not text:
            return 0
        try:
            count = self._client.models.count_tokens(
                model=self._model_name, contents=text
            ).total_tokens
            return count or 0
        except Exception as e:
            logger.warning(
                f"Token counting API failed: {e}. Falling back to heuristic."
            )
            return self._estimate_token_count(text)

    def get_token_limit(self) -> int:
        """
        Return the maximum number of tokens allowed per input prompt.

        Returns:
            int: Maximum token limit configured for Gemini client.
        """
        return self._max_tokens
