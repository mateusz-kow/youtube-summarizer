# YouTube Summarizer

[![CI](https://github.com/mateusz-kow/youtube-summarizer/actions/workflows/ci.yml/badge.svg)](https://github.com/mateusz-kow/youtube-summarizer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool to generate an AI-powered summary of any YouTube video using its subtitles.

## Overview

This tool provides a streamlined way to get the essence of a YouTube video without watching it. It fetches the video's English subtitles, processes them into clean text, and then uses Google's Gemini AI to generate a concise, narrative-style summary. It's designed to handle videos of any length by intelligently chunking long transcripts to work within the AI model's token limits.

The goal is not just to summarize, but to create a shortened version that reads like a well-crafted article, preserving key ideas, insights, and examples.

## Features

-   **AI-Powered Summaries**: Leverages the Google Gemini model for high-quality, coherent text generation.
-   **Intelligent Subtitle Handling**: Automatically downloads official English subtitles and falls back to auto-generated ones if necessary.
-   **Handles Long Videos**: Intelligently splits long transcripts into manageable chunks, processes them, and then combines the results for a final, comprehensive summary.
-   **Clean Transcript Processing**: Parses SRT subtitle files to remove timestamps, indices, and annotations (e.g., `[music]`, `[applause]`), ensuring the AI receives clean, relevant text.
-   **Flexible Output**: Print summaries directly to the console for a quick read or save them to a markdown file for later reference.
-   **Easy Configuration**: Uses a simple `.env` file to manage your Google AI API key and model preferences.

## Prerequisites

Before you begin, ensure you have the following installed:

-   [Python 3.11+](https://www.python.org/downloads/)
-   [Poetry](https://python-poetry.org/docs/#installation) (for dependency management)
-   A **Google AI API Key**. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Installation

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/mateusz-kow/youtube-summarizer.git
    cd youtube-summarizer
    ```

2.  **Install dependencies using Poetry:**

    This command will create a virtual environment and install all the required packages listed in `pyproject.toml`.

    ```sh
    poetry install
    ```

## Configuration

The application requires a Google AI API key to function.

1.  **Create a `.env` file:**

    Create a file named `.env` in the root of the project directory by copying the sample file:

    ```sh
    cp sample.env .env
    ```

2.  **Add your API key:**

    Open the `.env` file and replace `YOUR_API_KEY_HERE` with your actual Google AI API key. You can also customize the model and token limits if needed.

    ```dotenv
    # .env
    GOOGLE_API_KEY=YOUR_API_KEY_HERE
    GOOGLE_MODEL_NAME=gemma-3n-e4b-it
    GOOGLE_LLM_MAX_INPUT_TOKENS=6000
    ```

## Usage

You can run the script using `poetry run ytsum`.

### Basic Usage

To generate a summary and print it to the console, use the `-u` or `--url` flag followed by the YouTube video URL.

```sh
poetry run ytsum -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Saving to a File

To save the summary to a markdown file, use the `-o` or `--output-file` flag.

```sh
poetry run ytsum -u "https://www.youtube.com/watch?v=your_video_id" -o my_summary.md
```

### Verbose Mode

For more detailed logging output during the process, add the `-v` or `--verbose` flag.

```sh
poetry run ytsum -u "https://www.youtube.com/watch?v=your_video_id" -v
```

## Development and Contribution

We welcome contributions! The development environment is managed with Poetry, and code quality is maintained with several tools.

### Setting Up

Follow the [Installation](#installation) steps to set up the project and its dependencies. The `poetry install` command also installs all development dependencies.

### Running Quality Checks

This project uses `Ruff` for linting, `Black` for code formatting, `Mypy` for static type checking, and `Pytest` for tests. The CI pipeline validates these checks.

-   **Lint with Ruff:**

    ```sh
    poetry run ruff check .
    ```

-   **Format with Black:**

    ```sh
    poetry run black .
    ```

-   **Static Type Checking with Mypy:**

    ```sh
    poetry run mypy .
    ```

-   **Run Tests with Pytest:**

    ```sh
    poetry run pytest
    ```

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.