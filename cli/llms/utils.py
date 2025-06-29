from typing import Callable
import logging


logger = logging.getLogger(__name__)


def chunk_text(text: str,
               get_token_count: Callable,
               max_tokens: int,
               generate_prompt: Callable,
               estimate_token_count: Callable,
               *args) -> list[str]:
    """
    Splits text into chunks, ensuring no chunk exceeds the token limit.
    """
    sentences = text.split('. ')
    if not sentences:
        return []

    if len(sentences) == 1:
        sentence_text = sentences[0]
        actual_tokens = get_token_count(generate_prompt(sentence_text, *args))
        if actual_tokens > max_tokens:
            logger.warning(
                f"A single sentence of {actual_tokens} tokens exceeds the max limit of {max_tokens}. "
                "Returning it as a single, oversized chunk."
            )
            half = len(sentence_text) // 2

            first_half = sentence_text[:half]
            second_half = sentence_text[half:]
            return [first_half, second_half]

    initial_chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0

    for sentence in sentences:
        sentence_with_period = sentence if sentence.endswith('.') else sentence + '.'

        token_count = estimate_token_count(generate_prompt(sentence_with_period, *args))

        if current_chunk_tokens + token_count > max_tokens and current_chunk_sentences:
            initial_chunks.append(" ".join(current_chunk_sentences).strip())
            current_chunk_sentences = [sentence_with_period]
            current_chunk_tokens = token_count
        else:
            current_chunk_sentences.append(sentence_with_period)
            current_chunk_tokens += token_count

    if current_chunk_sentences:
        initial_chunks.append(" ".join(current_chunk_sentences).strip())

    logger.info(f"Initial split created {len(initial_chunks)} chunks using estimation. Now verifying...")

    final_chunks = []
    oversized_chunks_count = 0
    for chunk in initial_chunks:
        actual_token_count = get_token_count(generate_prompt(chunk, *args))

        if actual_token_count > max_tokens:
            oversized_chunks_count += 1
            logger.warning(
                f"Oversized chunk detected (estimated OK, but actual is {actual_token_count} > {max_tokens}). "
                f"Re-chunking it with the precise method."
            )

            sub_chunks = chunk_text(chunk,
                                    get_token_count=get_token_count,
                                    max_tokens=max_tokens,
                                    generate_prompt=generate_prompt,
                                    estimate_token_count=estimate_token_count,
                                    *args)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    if oversized_chunks_count > 0:
        logger.info(
            f"Verification complete. Re-split {oversized_chunks_count} oversized chunks. "
            f"Final chunk count: {len(final_chunks)}."
        )
    else:
        logger.info("Verification complete. All estimated chunks were within the token limit.")

    return final_chunks
