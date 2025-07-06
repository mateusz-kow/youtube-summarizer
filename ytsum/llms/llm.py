from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from logging import Logger

from ytsum.llms.utils import chunk_text
from ytsum.utils.prompts.prompt_factory import Prompt, get_prompt_generator


class LLM(ABC):
    """Abstract base class for language models used in summarization workflows."""

    def __init__(self, logger: Logger):
        """
        Initialize the LLM instance with a logger.

        Args:
            logger (Logger): Logger instance for capturing debug or runtime information.
        """
        self._logger = logger

    def ask_prompt(self, prompt_type: Prompt, text: str) -> str:
        """
        Construct and submit a prompt to the language model.

        If the input text exceeds the token limit, it is split into chunks and processed in parallel.

        Args:
            prompt_type (Prompt): The type of prompt to generate.
            text (str): Input text to query the model with.

        Returns:
            str: The model's response to the prompt.
        """
        prompt_generator = get_prompt_generator(prompt_type)
        prompt = prompt_generator(text)
        total_tokens = self.get_token_count(text)
        self._logger.debug(f"Total token count: {total_tokens}, prompt: {prompt}")

        if total_tokens <= self.get_token_limit():
            return self.ask(prompt)

        chunks = chunk_text(
            text=text,
            get_token_count=self.get_token_count,
            max_tokens=self.get_token_limit(),
            generate_prompt=prompt_generator,
            estimate_token_count=self._estimate_token_count,
        )

        self._logger.debug(f"Text split into {len(chunks)} chunks for summarization.")

        answers = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.ask, prompt_generator(chunk), 5, 30) for chunk in chunks]
            for future in futures:
                answers.append(future.result())

        combined_answers = "\n\n".join(answers)
        return self.ask_prompt(prompt_type, combined_answers)

    @abstractmethod
    def ask(self, prompt: str, max_retries: int = 5, backoff_seconds: int = 30) -> str:
        """
        Submit a prompt to the model and return its response.

        Args:
            prompt (str): The prompt to send to the model.
            max_retries (int): Number of times to retry on failure. Defaults to 5.
            backoff_seconds (int): Seconds to wait between retries. Defaults to 30.

        Returns:
            str: The model's response.
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Return the token count of a given string according to the model's tokenizer.

        Args:
            text (str): The input text.

        Returns:
            int: The number of tokens.
        """
        pass

    @staticmethod
    def _estimate_token_count(text: str) -> int:
        """
        Estimate the number of tokens using a heuristic.

        Args:
            text (str): The input text.

        Returns:
            int: Estimated token count.
        """
        return max(len(text) // 4, 1)

    @abstractmethod
    def get_token_limit(self) -> int:
        """
        Return the maximum number of tokens the model can handle.

        Returns:
            int: Token limit for a single input.
        """
        pass
