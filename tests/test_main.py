from argparse import Namespace
from collections.abc import Generator
from unittest.mock import MagicMock, mock_open, patch

import pytest

from ytsum.__main__ import main
from ytsum.utils.prompts.prompt_factory import Prompt


@pytest.fixture
def mock_dependencies() -> Generator[dict[str, MagicMock], None, None]:
    """Fixture to mock all major dependencies of main()."""
    with (
        patch("ytsum.__main__.get_args") as mock_get_args,
        patch("ytsum.__main__.configure_logging") as mock_configure_logging,
        patch("ytsum.__main__.get_video_name") as mock_get_video_name,
        patch("ytsum.__main__.get_video_subtitles") as mock_get_video_subtitles,
        patch("ytsum.__main__.Gemini") as mock_gemini,
    ):

        mock_get_video_name.return_value = "Test Video Title"
        mock_get_video_subtitles.return_value = "some subtitle text"

        mock_gemini_instance = MagicMock()
        mock_gemini_instance.ask_prompt.return_value = "AI-generated summary."
        mock_gemini.return_value = mock_gemini_instance

        yield {
            "get_args": mock_get_args,
            "configure_logging": mock_configure_logging,
            "get_video_name": mock_get_video_name,
            "get_video_subtitles": mock_get_video_subtitles,
            "Gemini": mock_gemini,
            "gemini_instance": mock_gemini_instance,
        }


def test_main_prints_to_stdout_by_default(mock_dependencies: dict[str, MagicMock]) -> None:
    """Tests the default behavior of printing the summary to stdout."""
    video_url = "https://a.test.url"
    mock_dependencies["get_args"].return_value = Namespace(url=video_url, output_file=None, verbose=False)

    with patch("sys.stdout.write") as mock_stdout:
        main()

        mock_dependencies["configure_logging"].assert_called_once_with(False)
        mock_dependencies["get_video_subtitles"].assert_called_once_with(video_url)
        mock_dependencies["gemini_instance"].ask_prompt.assert_called_once_with(Prompt.SUMMARY, "some subtitle text")
        expected_output = "AI-generated summary.\n\nOriginal video: [**Test Video Title**](https://a.test.url)\n"
        mock_stdout.assert_called_once_with(expected_output)


def test_main_saves_to_output_file(mock_dependencies: dict[str, MagicMock]) -> None:
    """Tests saving the summary to a file when --output-file is provided."""
    output_filename = "summary.md"
    mock_dependencies["get_args"].return_value = Namespace(
        url="https://a.test.url", output_file=output_filename, verbose=True
    )

    m = mock_open()
    with patch("builtins.open", m):
        main()

        mock_dependencies["configure_logging"].assert_called_once_with(True)
        m.assert_called_once_with(output_filename, "w", encoding="utf-8")
        handle = m()
        expected_output = "AI-generated summary.\n\nOriginal video: [**Test Video Title**](https://a.test.url)\n"
        handle.write.assert_called_once_with(expected_output)
