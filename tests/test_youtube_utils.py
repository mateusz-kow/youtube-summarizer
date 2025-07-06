import pytest
from ytsum.youtube.utils import get_raw_text_from_srt

SRT_STANDARD = "1\n00:00:01,000 --> 00:00:03,000\nFirst subtitle.\n\n2\n00:00:04,500 --> 00:00:06,800\nSecond\nmulti-line subtitle."
SRT_WITH_ANNOTATIONS = (
    "1\n00:00:10,000 --> 00:00:12,000\n[music] Let's begin. [applause]"
)


@pytest.mark.parametrize(
    "srt_input, expected_output",
    [
        (SRT_STANDARD, "First subtitle. Second multi-line subtitle."),
        (SRT_WITH_ANNOTATIONS, "Let's begin."),
        ("", ""),
        ("Malformed text", ""),
    ],
)
def test_get_raw_text_from_srt(srt_input, expected_output):
    """Parses SRT to raw text."""
    assert get_raw_text_from_srt(srt_input) == expected_output
