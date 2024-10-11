# tts-joinery

tts-joinery is a Python library and CLI tool to work around length limitations in text-to-speech APIs.

Since currently-popular APIs are limited to 4096 characters, this library will:

-   Chunk the input text into sentences using the [NLTK Punkt module](https://www.nltk.org/api/nltk.tokenize.punkt.html) (for better audio by avoiding segments split in the middle of a word or sentence).
-   Run each chunk through the TTS API
-   Join together the resulting output to produce a single MP3 file

Currently only the OpenAI API is supported, with the intent to add more in the future.

## Installation

```bash
pip install tts-joinery
```

or use `pipx` to install as a standalone tool.

**Requires ffmpeg** for the audio file processing.

Installation may vary depending on your system. On Linux you can use your system package manager. On Mac `brew install ffmpeg` should work.

## Usage

### Command-Line Interface (CLI)

The CLI expects to find an OpenAI API Key in a `OPENAI_API_KEY` environment variable, or in a .env file.

#### Syntax

```
ttsjoin [OPTIONS] [COMMAND]
```

#### Options

```
Options:
--input-file FILENAME   Plaintext file to process into speech, otherwise stdin
--output-file FILENAME  MP3 result, otherwise stdout
--model TEXT            Slug of the text-to-speech model to be used
--service TEXT          API service (currently only supports openai)
--voice TEXT            Slug of the voice to be used
--no-cache BOOLEAN      Disable caching
--help                  Show this message and exit.

Commands:
  cache [clear, show]
```

#### Examples

1. Using an input file and specifying an output file:

```bash
ttsjoin --input-file input.txt --output-file output.mp3 --model tts-1 --service openai --voice onyx
```

2. Using stdin and stdout with default options:

```bash
echo "Your text to be processed" | ttsjoin > output.mp3
```

3. Each chunk of text is cached for performance when running the same text multiple times, this can be disabled:

```bash
ttsjoin --input-file input.txt --output-file output.mp3 --no-cache
```

5. Clear cache directory

```bash
ttsjoin cache clear
```

### Python Library

You can also use tts-joinery as part of your Python project:

```python
import nltk

from joinery.op import JoinOp
from joinery.api.openai import OpenAIApi

# Only need to download once, handled for you automatically in the CLI
nltk.download('punkt_tab', quiet=True)

tts = JoinOp(
    text='This is only a test!',
    api=OpenAIApi(
        model='tts-1-hd',
        voice='onyx',
        api_key=OPENAI_API_KEY,
    ),
)

tts.process_to_file('output.mp3')
```

## Changelog

#### v1.0.4 (2024-10-11)

-   Fixed issue with nltk dependency [#4](https://github.com/drien/tts-joinery/issues/5)
-   Model, voice, and service CLI params are now case-insensitive

#### v1.0.3 (2024-10-05)

-   Added cache management commands to cli
-   Fixed a bug when running
-   Added end-to-end tests

#### v1.0.2 (2024-10-03)

-   Fixed crash when running with caching disabled (#3)

## Contributing

Contributions welcome, particularly other TTS APIs, check the issues beforehand and feel free to open a PR. Code is formatted with Black.

Test can be run manually. Suite includes end-to-end tests with live API calls, ensure you have an OPENAI_API_KEY set in `.env.test`, and run `pytest`. You can install development dependencies with `pip install -e .[test]`

## Contributors

Special thanks to:

-   [Mayank Vishwakarma](mailto:mayank@mynk.me) (@mayankwebbing)

## License

This project is licensed under the MIT License.

Copyright 2024, Adrien Delessert
