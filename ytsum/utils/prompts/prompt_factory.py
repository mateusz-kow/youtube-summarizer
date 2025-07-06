"""
Prompt factory module for mapping prompt types to their respective generator functions.
"""

from enum import IntEnum, auto
from typing import Callable

from ytsum.utils.prompts.prompt_generators import generate_summary_prompt


class Prompt(IntEnum):
    """
    Enumeration of supported prompt types.
    """

    SUMMARY = auto()


PROMPT_TO_GENERATOR: dict[Prompt, Callable] = {
    Prompt.SUMMARY: generate_summary_prompt,
}


def get_prompt_generator(prompt: Prompt) -> Callable:
    """
    Retrieves the generator function associated with a given prompt type.

    Args:
        prompt (Prompt): The prompt type to retrieve a generator for.

    Returns:
        Callable: The corresponding prompt generator function.

    Raises:
        NotImplementedError: If the prompt type is not supported.
    """
    try:
        return PROMPT_TO_GENERATOR[prompt]
    except KeyError:
        raise NotImplementedError(f"Prompt {prompt} not implemented")
