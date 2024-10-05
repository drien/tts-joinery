import os
import pytest
import subprocess
import time

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from pydub import AudioSegment

from joinery.op import JoinOp
from joinery.api.openai import OpenAIApi

load_dotenv(find_dotenv(".env.test"))


@pytest.fixture
def api():
    return OpenAIApi(model="tts-1", voice="alloy")


@pytest.fixture
def short_text():
    return "This is a short test sentence."


@pytest.fixture
def long_text():
    return "This is a very long text. " * 200  # 5200 char


def test_direct_usage_short_text(api, short_text, tmp_path):
    output_file = tmp_path / "output_short.mp3"
    op = JoinOp(short_text, api)
    op.process_to_file(output_file)

    assert output_file.exists()
    audio = AudioSegment.from_mp3(output_file)
    assert len(audio) > 0  # Check if audio has content


def test_direct_usage_long_text(api, long_text, tmp_path):
    output_file = tmp_path / "output_long.mp3"
    op = JoinOp(long_text, api)
    op.process_to_file(output_file)

    assert output_file.exists()
    audio = AudioSegment.from_mp3(output_file)
    assert len(audio) > 0  # Check if audio has content


def test_cli_short_text(short_text, tmp_path):
    input_file = tmp_path / "input_short.txt"
    output_file = tmp_path / "output_short.mp3"

    input_file.write_text(short_text)

    result = subprocess.run(
        ["ttsjoin", "--input-file", str(input_file), "--output-file", str(output_file)]
    )
    assert result.returncode == 0

    assert output_file.exists()
    audio = AudioSegment.from_mp3(output_file)
    assert len(audio) > 0


def test_cli_long_text(long_text, tmp_path):
    input_file = tmp_path / "input_long.txt"
    output_file = tmp_path / "output_long.mp3"

    input_file.write_text(long_text)

    result = subprocess.run(
        ["ttsjoin", "--input-file", str(input_file), "--output-file", str(output_file)]
    )
    assert result.returncode == 0

    assert output_file.exists()
    audio = AudioSegment.from_mp3(output_file)
    assert len(audio) > 0


def test_caching_enabled(api, short_text, tmp_path):
    op = JoinOp(short_text, api)

    api.clear_cache()

    # First run
    start_time = time.time()
    op.process_to_file(tmp_path / "output1.mp3")
    first_run_time = time.time() - start_time

    # Check cache directory
    cache_files = list(
        Path(api.CACHE_DIR).glob(f"{api.service}_{api.model}_{api.voice}_*.mp3")
    )
    assert len(cache_files) > 0
    # Second run
    start_time = time.time()
    op.process_to_file(tmp_path / "output2.mp3")
    second_run_time = time.time() - start_time

    # The second run should be significantly faster due to caching
    assert second_run_time < first_run_time / 2


def test_caching_disabled(api, short_text, tmp_path):
    api.caching_enabled = False
    op = JoinOp(short_text, api)

    api.clear_cache()

    # First run
    op.process_to_file(tmp_path / "output1.mp3")

    # Check cache directory
    cache_files_before = set(
        Path(api.CACHE_DIR).glob(f"{api.service}_{api.model}_{api.voice}_*.mp3")
    )
    mtimes_before = [os.path.getmtime(i) for i in cache_files_before]

    # Second run
    op.process_to_file(tmp_path / "output2.mp3")

    # Check cache directory again
    cache_files_after = set(
        Path(api.CACHE_DIR).glob(f"{api.service}_{api.model}_{api.voice}_*.mp3")
    )
    mtimes_after = [os.path.getmtime(i) for i in cache_files_after]

    # All cache files should be rewritten
    assert all([n > mtimes_before[i] for i, n in enumerate(mtimes_after)])


def test_cli_no_cache(short_text, tmp_path):
    input_file = tmp_path / "input_no_cache.txt"
    output_file1 = tmp_path / "output1_no_cache.mp3"
    output_file2 = tmp_path / "output2_no_cache.mp3"

    input_file.write_text(short_text)

    # First run
    subprocess.run(
        [
            "ttsjoin",
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_file1),
            "--no-cache",
        ]
    )

    # Check cache directory
    cache_dir = Path(os.path.expanduser("~/.local/share/tts_joinery"))
    cache_files_before = set(cache_dir.glob("openai_tts-1_alloy_*.mp3"))
    mtimes_before = [os.path.getmtime(i) for i in cache_files_before]

    # Second run
    subprocess.run(
        [
            "ttsjoin",
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_file2),
            "--no-cache",
        ]
    )

    # Check cache directory again
    cache_files_after = set(cache_dir.glob("openai_tts-1_alloy_*.mp3"))
    mtimes_after = [os.path.getmtime(i) for i in cache_files_after]

    assert all([n > mtimes_before[i] for i, n in enumerate(mtimes_after)])

    # Both output files should exist and have content
    assert output_file1.exists() and output_file1.stat().st_size > 0
    assert output_file2.exists() and output_file2.stat().st_size > 0
