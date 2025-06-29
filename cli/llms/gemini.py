import logging
import os
import time

from google import genai
from google.genai.errors import ClientError

from cli.llms.llm import LLM

logger = logging.getLogger(__name__)


class Gemini(LLM):
    def __init__(self, max_tokens: int = 6000):
        super().__init__(logger)
        self._max_tokens = max_tokens
        self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self._model_name = "gemma-3n-e4b-it"
        logger.info(f"Gemini initialized with max token limit: {self._max_tokens}")

    def ask(self, prompt: str, max_retries: int = 5, backoff_seconds: int = 30) -> str:
        tokens = self.get_token_count(prompt)
        logger.debug(f"Calling Gemini with prompt: {prompt} and tokens {tokens}")

        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.models.generate_content(model=self._model_name, contents=prompt)
                return response.text.strip()
            except ClientError as e:
                error_msg = str(e)
                if "RESOURCE_EXHAUSTED" in error_msg:
                    logger.warning(f"Quota exceeded (attempt {attempt}/{max_retries}). "
                                   f"Retrying in {backoff_seconds} seconds...")
                    time.sleep(backoff_seconds)
                else:
                    logger.error(f"Unexpected API error: {e}")
                    raise

        raise RuntimeError("Failed to get response after multiple retries due to quota exhaustion.")

    def get_token_count(self, text: str) -> int:
        """
        Approximate token count for the provided text using the model's token counting API.
        Falls back to a rough estimate if the API call fails.
        """
        if not text:
            return 0
        try:
            count = self._client.models.count_tokens(model=self._model_name, contents=text).total_tokens
            return count or 0
        except Exception as e:
            logger.warning(f"Token counting API failed: {e}. Falling back to heuristic.")
            return self._estimate_token_count(text)

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimates token count heuristically as length of text divided by 4.
        """
        return max(len(text) // 4, 1)

    def get_token_limit(self) -> int:
        """
        Returns the maximum allowed tokens for input prompt.
        """
        return self._max_tokens
