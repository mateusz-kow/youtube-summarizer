# tests/test_youtube_manager.py
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from ytsum.youtube.youtube_manager import get_video_name, get_video_subtitles

YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@patch("yt_dlp.YoutubeDL")
def test_get_video_name_success(mock_youtube_dl: MagicMock) -> None:
    """Tests successful retrieval of a video title."""
    mock_instance = mock_youtube_dl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"title": "Test Video Title"}

    title = get_video_name(YOUTUBE_URL)

    assert title == "Test Video Title"
    mock_instance.extract_info.assert_called_once_with(YOUTUBE_URL, download=False)


@patch("yt_dlp.YoutubeDL")
def test_get_video_name_failure(mock_youtube_dl: MagicMock) -> None:
    """Tests failure case when video info cannot be extracted."""
    mock_instance = mock_youtube_dl.return_value.__enter__.return_value
    mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Test Error")

    with pytest.raises(RuntimeError):
        get_video_name(YOUTUBE_URL)


@patch("ytsum.youtube.youtube_manager.get_raw_text_from_srt", return_value="Cleaned Subtitles")
@patch("builtins.open")
@patch("glob.glob")
@patch("yt_dlp.YoutubeDL")
def test_get_video_subtitles_official_found(
    mock_youtube_dl: MagicMock, mock_glob: MagicMock, mock_open: MagicMock, mock_get_raw: MagicMock
) -> None:
    """Tests finding official English subtitles successfully."""
    mock_glob.return_value = ["/tmp/subs.en.srt"]
    mock_youtube_dl_instance = mock_youtube_dl.return_value.__enter__.return_value

    result = get_video_subtitles(YOUTUBE_URL)

    assert result == "Cleaned Subtitles"

    mock_youtube_dl_instance.download.assert_called_once_with([YOUTUBE_URL])
    mock_glob.assert_called_once()
    mock_open.assert_called_once_with("/tmp/subs.en.srt", encoding="utf-8")
    mock_get_raw.assert_called_once()


@patch("glob.glob", return_value=[])
@patch("yt_dlp.YoutubeDL")
def test_get_video_subtitles_none_found(mock_youtube_dl: MagicMock, mock_glob: MagicMock) -> None:
    """Tests the case where no subtitles (official or auto) are found."""
    mock_youtube_dl_instance = mock_youtube_dl.return_value.__enter__.return_value

    result = get_video_subtitles(YOUTUBE_URL)

    assert result is None
    assert mock_youtube_dl_instance.download.call_count == 2
    assert mock_glob.call_count == 2
