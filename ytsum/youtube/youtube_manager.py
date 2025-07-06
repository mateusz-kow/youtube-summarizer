import glob
import logging
import os
import tempfile

import yt_dlp

from ytsum.youtube.utils import get_raw_text_from_srt

logger = logging.getLogger(__name__)


def get_video_subtitles(youtube_url: str) -> str | None:
    """
    Downloads English subtitles or auto-generated English subtitles (including en variants like en-GB, en-US)
    from a YouTube video URL. Returns the subtitle content as a string, or None if no subtitles are available.
    """
    logger.info(f"Starting subtitle download for URL: {youtube_url}")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "subs")

        def find_srt_file() -> str | None:
            matches = glob.glob(os.path.join(tmpdir, "subs.en*.srt"))
            if matches:
                logger.info(f"Found subtitle file: {matches[0]}")
                return matches[0]
            return None

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": True,
            "subtitleslangs": ["en.*"],  # Match all English variants
            "subtitlesformat": "srt",
            "skip_download": True,
            "outtmpl": f"{base_path}.%(ext)s",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Attempt to download official subtitles
                logger.info("Attempting to download official English subtitles...")
                ydl.download([youtube_url])

                subs_file = find_srt_file()

                # Try auto-generated subtitles if no official subtitles are found
                if subs_file is None:
                    logger.info("Official subtitles not found. Trying auto-generated subtitles...")
                    ydl_opts["writeautomaticsub"] = True
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_auto:
                        ydl_auto.download([youtube_url])
                        subs_file = find_srt_file()

                if subs_file is None:
                    logger.info("No subtitles found.")
                    return None

                with open(subs_file, encoding="utf-8") as f:
                    content = f.read()
                    logger.info(f"Successfully read subtitles from {subs_file} (size: {len(content)} characters).")
                    logger.debug(content)
                    return get_raw_text_from_srt(content)

        except Exception as e:
            logger.error(f"Error downloading subtitles for {youtube_url}: {e}")
            return None


def get_video_name(url: str) -> str:
    """
    Retrieves the title of a YouTube video without downloading the content.

    :param url: URL of the YouTube video
    :return: Title of the video as a string
    """
    logger.info(f"Fetching video title for URL: {url}")

    class QuietLogger:
        """Custom logger to suppress yt-dlp output."""

        def debug(self, msg: str) -> None:
            pass

        def warning(self, msg: str) -> None:
            pass

        def error(self, msg: str) -> None:
            pass

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "nocheckcertificate": True,
        "logger": QuietLogger(),  # Suppress yt-dlp logs
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict is None:
                raise RuntimeError(f"Could not extract video info for URL: {url}")
            title = info_dict.get("title")
            if not title:
                raise ValueError(f"No title found in video metadata for URL: {url}")
            logger.info(f"Retrieved video title: {title}")
            return str(title)
    except Exception as e:
        raise RuntimeError(f"Error fetching video title for {url}: {e}") from e
