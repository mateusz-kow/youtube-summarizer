from enum import Enum
from typing import Callable

from cli.utils.prompts.prompt_generators import generate_summary_prompt


class Prompt(Enum):
    SUMMARY = "sum"


PROMPT_TO_GENERATOR: dict[Prompt, Callable] = {
    Prompt.SUMMARY: generate_summary_prompt,
}


def get_prompt_generator(prompt: Prompt) -> Callable:
    try:
        return PROMPT_TO_GENERATOR[prompt]
    except KeyError:
        raise NotImplementedError(f"Prompt {prompt} not implemented")
