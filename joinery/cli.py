import click
import nltk
import shutil
import sys
import tempfile

from dotenv import load_dotenv

from joinery.api import API_BY_SERVICE_SLUG
from joinery.op import JoinOp

load_dotenv()


@click.command()
@click.option(
    "--input-file",
    help="Plaintext file to process into speech, otherwise stdin",
    default=sys.stdin,
    type=click.File(),
)
@click.option(
    "--output-file",
    help="MP3 result, otherwise stdout",
    default=sys.stdout,
    type=click.File("wb+"),
)
@click.option(
    "--model", default="tts-1", help="Slug of the text-to-speech model to be used"
)
@click.option(
    "--service", default="openai", help="API service (currently only supports openai)"
)
@click.option("--voice", default="alloy", help="Slug of the voice to be used")
@click.option("--no-cache", default=False, help="Disable caching")
def run_tts(input_file, output_file, model, service, voice, no_cache):
    nltk.download("punkt", quiet=True)

    if input_file.name == "<stdin>" and sys.stdout.isatty():
        click.echo(
            click.style(
                "Reading input text from stdin...use --input-file to specify a file to read instead.",
                fg="yellow",
            ),
            err=True,
        )

    text = input_file.read()
    if not text:
        click.echo(
            click.style(
                "Empty input.",
                fg="red",
            ),
            err=True,
        )
        return

    if output_file.name == "<stdout>" and sys.stdout.isatty():
        click.echo(
            click.style(
                "Refusing to write binary output to your terminal, redirect output or specify --output-file.",
                fg="red",
            ),
            err=True,
        )
        return

    op = JoinOp(
        text,
        api=API_BY_SERVICE_SLUG[service](model, voice, caching_enabled=(not no_cache)),
    )
    sentences = op.tokenize()
    with click.progressbar(
        sentences, label="Chunking sentences", file=sys.stderr
    ) as sentence_list:
        for sentence in sentence_list:
            op.add_to_chunks(sentence)

    chunks = op.chunked_text()
    click.echo(
        f"Preparing to run TTS in {len(chunks)} chunks...({list(map(len, chunks))})",
        err=True,
    )

    outputs = []
    with click.progressbar(
        chunks, label="Running chunked TTS", file=sys.stderr
    ) as chunks:
        for chunk in chunks:
            outputs.append(op.run_tts(chunk))

    joined = None
    with click.progressbar(
        outputs, label="Processing audio files", file=sys.stderr
    ) as output_files:
        for file in output_files:
            joined = op.join_audio(file, append_to=joined)

    click.echo("Finalizing...", err=True)

    if output_file.name == "<stdout>":
        tmpfile, tmppath = tempfile.mkstemp()
        joined.export(tmppath, format="mp3")
        with open(tmppath, "rb") as f:
            shutil.copyfileobj(f, output_file.buffer)
    else:
        joined.export(output_file, format="mp3")


if __name__ == "__main__":
    run_tts()
