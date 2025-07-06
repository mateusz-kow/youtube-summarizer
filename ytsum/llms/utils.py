from typing import Callable
import logging
from nltk.tokenize import sent_tokenize
import subprocess
import sys


def silent_nltk_download(resource_name):
    """
    Silently download an NLTK resource without printing to stdout or stderr.

    This function runs a separate Python subprocess to download the specified
    NLTK resource, while suppressing any output generated during the download.

    Args:
        resource_name (str): The name of the NLTK resource to download.
    """

    subprocess.run(
        [sys.executable, "-c", f"import nltk; nltk.download('{resource_name}')"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


silent_nltk_download("punkt_tab")
logger = logging.getLogger(__name__)


def chunk_text(
    *,
    text: str,
    get_token_count: Callable,
    max_tokens: int,
    generate_prompt: Callable,
    estimate_token_count: Callable,
) -> list[str]:
    """
    Splits text into chunks using nltk sentence tokenizer,
    ensuring no chunk exceeds the token limit.
    """
    sentences = sent_tokenize(text)
    if not sentences:
        return []

    if len(sentences) == 1:
        sentence_text = sentences[0]
        actual_tokens = get_token_count(generate_prompt(sentence_text))
        if actual_tokens > max_tokens:
            logger.warning(
                f"A single sentence of {actual_tokens} tokens exceeds the max limit of {max_tokens}. "
                "Returning it as a single, oversized chunk."
            )
            half = len(sentence_text) // 2
            return [sentence_text[:half], sentence_text[half:]]

    initial_chunks: list[str] = []
    current_chunk_sentences: list[str] = []
    current_chunk_tokens = 0

    for sentence in sentences:
        token_count = estimate_token_count(generate_prompt(sentence))

        if current_chunk_tokens + token_count > max_tokens and current_chunk_sentences:
            initial_chunks.append(" ".join(current_chunk_sentences).strip())
            current_chunk_sentences = [sentence]
            current_chunk_tokens = token_count
        else:
            current_chunk_sentences.append(sentence)
            current_chunk_tokens += token_count

    if current_chunk_sentences:
        initial_chunks.append(" ".join(current_chunk_sentences).strip())

    logger.info(
        f"Initial split created {len(initial_chunks)} chunks using estimation. Now verifying..."
    )

    final_chunks = []
    oversized_chunks_count = 0

    for chunk in initial_chunks:
        actual_token_count = get_token_count(generate_prompt(chunk))

        if actual_token_count > max_tokens:
            oversized_chunks_count += 1
            logger.warning(
                f"Oversized chunk detected (estimated OK, but actual is {actual_token_count} > {max_tokens}). "
                "Re-chunking it with the precise method."
            )
            sub_chunks = chunk_text(
                text=chunk,
                get_token_count=get_token_count,
                max_tokens=max_tokens,
                generate_prompt=generate_prompt,
                estimate_token_count=estimate_token_count,
            )
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    if oversized_chunks_count > 0:
        logger.info(
            f"Verification complete. Re-split {oversized_chunks_count} oversized chunks. "
            f"Final chunk count: {len(final_chunks)}."
        )
    else:
        logger.info(
            "Verification complete. All estimated chunks were within the token limit."
        )

    return final_chunks
