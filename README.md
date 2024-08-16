# tts-joinery

tts-joinery is a Python library and CLI tool to work around length limitations in text-to-speech APIs.

Since currently-popular APIs are limited to 4096 characters, this library will:

-   Chunk the input text into sentences using the [NLTK Punkt module](https://www.nltk.org/api/nltk.tokenize.punkt.html)
-   Run each chunk through the TTS API
-   Join together the resulting output to produce a single MP3 file

Currently only the OpenAI API is supported, with the intent to add more in the future.

## Installation

```bash
pip install tts-joinery
```

or use `pipx` to install as a standalone tool.

## Usage

### Command-Line Interface (CLI)

#### Syntax

```
ttsjoin [OPTIONS]
```

#### Options

```
--input-file FILENAME   Plaintext file to process into speech, otherwise stdin
--output-file FILENAME  MP3 result, otherwise stdout
--model TEXT            Slug of the text-to-speech model to be used
--service TEXT          API service (currently only supports openai)
--voice TEXT            Slug of the voice to be used
--no-cache BOOLEAN      Disable caching
--help                  Show this message and exit.
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

3. Each chunk of text is cached for performance when the same text multiple times, this can be disabled:

```bash
ttsjoin --input-file input.txt --output-file output.mp3 --no-cache
```

### Python Library

You can also use tts-joinery as part of your Python project:

```python
from tts_joinery.op import JoinOp
from tts_joinery.api.openai import OpenAIApi

# Initialize the TTSJoinery with parameters
tts = JoinOp(
    text='This is only a test!',
    api=OpenAIApi(
        model='tts-1-hd',
        voice='onyx'
    ),
)

# Process the text to file
tts.process_to_file('output.mp3')
```

## Contributing

Contributions welcome, particularly other TTS APIs, check the issues beforehand and feel free to open a PR. Code is formatted with Black.

## License

This project is licensed under the MIT License.

Copyright 2024, Adrien Delessert
