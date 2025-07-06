import logging
import sys

from ytsum.config import APP_NAME
from ytsum.llms.gemini import Gemini
from ytsum.utils.input_parser import get_args
from ytsum.utils.logging_config import configure_logging
from ytsum.utils.prompts.prompt_factory import Prompt
from ytsum.youtube.youtube_manager import get_video_name, get_video_subtitles

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Executes the end-to-end process of retrieving subtitles from a YouTube video,
    generating a summary using an LLM, and writing the result to a file or standard output.

    Workflow:
        1. Parse CLI arguments including video URL and output file path.
        2. Retrieve the title of the YouTube video.
        3. Fetch subtitles for the given video.
        4. Generate a summary using the Gemini LLM based on the transcript.
        5. Write the summary to the specified output file or print to stdout.

    Raises:
        RuntimeError: If subtitles cannot be retrieved.
        Exception: For any unexpected error during processing.
    """
    try:
        args = get_args()
        configure_logging(args.verbose)
        video_url = args.url
        output_file = args.output_file

        logger.info(f"Starting application: {APP_NAME}")
        logger.debug(f"Video URL: {video_url}")
        logger.debug(f"Output file: {output_file}")

        video_title = get_video_name(video_url)

        subtitles = get_video_subtitles(video_url)
        if not subtitles:
            raise RuntimeError(f"Failed to retrieve subtitles from video: {video_url}")

        llm = Gemini()
        summary = llm.ask_prompt(Prompt.SUMMARY, subtitles)
        summary_text = summary + f"\n\nOriginal video: [**{video_title}**]({video_url})\n"

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(summary_text)
            logger.info(f"Summary saved to: {output_file}")
        else:
            sys.stdout.write(summary_text)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        print("Process interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception(f"An unknown error occurred during execution: {e}")
        print(e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
