def generate_summary_prompt(text: str) -> str:
    """
    Generate a structured prompt for the summarization request.
    """
    return (
        "Rewrite the following transcription into a concise, coherent, "
        "and engaging narrative that preserves all key ideas, insights, and examples from the video. "
        "Do not just summarize — create a shortened version that reads like a well-crafted article or essay. "
        "Include relevant expert commentary, detailed examples, and clear explanations where applicable. "
        "Exclude advertisements, CTA's, promotional content, and any non-essential information. "
        "Ensure the structure is logical and the flow natural, making it easy and enjoyable to read."
        "\nTranscription:"
        f"\n{text}"
    )
