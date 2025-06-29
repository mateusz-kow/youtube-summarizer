from logging import Logger
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from cli.utils.prompts.prompt_factory import Prompt, get_prompt_generator
from cli.llms.utils import chunk_text


class LLM(ABC):
    def __init__(self, logger: Logger):
        """
        Initializes the LLM with a maximum token limit and sets up the client.
        """
        self._logger = logger

    def ask_prompt(self, prompt_type: Prompt, text: str, *args) -> str:
        """
        Asks a question using the LLM model, handling quota exhaustion with retries.
        """
        prompt_generator = get_prompt_generator(prompt_type)
        prompt = prompt_generator(text, *args)
        total_tokens = self.get_token_count(text)
        self._logger.debug(f"Total token count: {total_tokens}, prompt: {prompt}")

        if total_tokens <= self.get_token_limit():
            return self.ask(prompt)

        chunks = chunk_text(text=text,
                            get_token_count=self.get_token_count,
                            max_tokens=self.get_token_limit(),
                            generate_prompt=prompt_generator,
                            estimate_token_count=self._estimate_token_count,
                            *args)

        self._logger.debug(f"Text split into {len(chunks)} chunks for summarization.")

        answers = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.ask,
                                       prompt_generator(chunk, *args),
                                       5,
                                       30) for chunk in chunks]
            for future in futures:
                answers.append(future.result())

        combined_answers = "\n\n".join(answers)
        return self.ask_prompt(prompt_type, combined_answers, *args)

    @abstractmethod
    def ask(self, prompt: str, max_retries: int = 5, backoff_seconds: int = 30) -> str:
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Approximate token count for the provided text using the model's token counting API.
        Falls back to a rough estimate if the API call fails.
        """
        pass

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimates token count heuristically as length of text divided by 4.
        """
        return self.get_token_count(text)

    @abstractmethod
    def get_token_limit(self) -> int:
        """
        Returns the maximum allowed tokens for input prompt.
        """
        pass
