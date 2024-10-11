import click
import glob
import nltk
import os
import shutil
import sys
import tempfile

from dotenv import load_dotenv

from joinery.api import API_BY_SERVICE_SLUG
from joinery.op import JoinOp

load_dotenv()


def _force_lowercase(ctx, param, value):
    if value is not None:
        return value.lower()


@click.group(invoke_without_command=True)
@click.pass_context
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
    "--model",
    default="tts-1",
    help="Slug of the text-to-speech model to be used",
    callback=_force_lowercase,
)
@click.option(
    "--service",
    default="openai",
    help="API service (currently only supports openai)",
    callback=_force_lowercase,
)
@click.option(
    "--voice",
    default="alloy",
    help="Slug of the voice to be used",
    callback=_force_lowercase,
)
@click.option("--no-cache", is_flag=True, default=False, help="Disable caching")
def run_tts(ctx, input_file, output_file, model, service, voice, no_cache):
    if ctx.invoked_subcommand:
        return

    nltk.download("punkt_tab", quiet=True)

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


@run_tts.group("cache")
def cache():
    pass


def _cache_dir():
    return list(API_BY_SERVICE_SLUG.values())[
        0
    ]().CACHE_DIR  # Assume cache dir never overridden? Eh.


@cache.command()
def show():
    click.echo(
        _cache_dir(),
        err=True,
    )


@cache.command()
def clear():
    cache_dir = _cache_dir()
    click.echo(
        click.style(f"Clearing files from {cache_dir}...", fg="yellow"),
        err=True,
    )
    files = glob.glob(f"{cache_dir}/*")
    for f in files:
        os.remove(f)
        click.echo(f"Removed {f}", err=True)


if __name__ == "__main__":
    run_tts()
