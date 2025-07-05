# tests/utils/prompts/test_prompt_factory.py

import pytest
from ytsum.utils.prompts.prompt_factory import Prompt, get_prompt_generator
from ytsum.utils.prompts.prompt_generators import generate_summary_prompt


def test_get_prompt_generator_summary():
    """Returns summary generator for SUMMARY."""
    assert get_prompt_generator(Prompt.SUMMARY) is generate_summary_prompt


def test_get_prompt_generator_not_implemented():
    """Raises if prompt type not implemented."""
    with pytest.raises(NotImplementedError):
        get_prompt_generator("invalid_prompt_type")
