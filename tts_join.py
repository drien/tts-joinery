import click
import glob
import hashlib
import nltk
import os
import re

from openai import OpenAI
from platformdirs import user_data_dir
from pydub import AudioSegment


CACHE_DIR = user_data_dir('tts_joinery', 'com.drien')
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

@click.command()
@click.option('--input_file', default='./tts_input.txt')
@click.option('--model', default='tts-1-hd')
@click.option('--service', default='openai')
@click.option('--voice', default='alloy')
def run_tts(input_file, model, service, voice):
    nltk.download('punkt')

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    chunked_input = [[]]
    i = 0
    with open(input_file, 'r') as input_file:
        sentences = nltk.sent_tokenize(input_file.read())
        with click.progressbar(sentences, label='Chunking sentences') as sentence_list:
            for sentence in sentence_list:
                if sum(map(len, chunked_input[i])) + len(chunked_input[i]) + len(sentence) < 4096:
                    chunked_input[i].append(sentence)
                else:
                    i += 1
                    chunked_input.append([sentence]) # Will fail for sentences > 4096 chars

    chunked_input = [' '.join(a) for a in chunked_input]

    print(f'Preparing to run TTS in {len(chunked_input)} chunks...({list(map(len, chunked_input))})')

    outputs = []
    with click.progressbar(chunked_input, label='Running chunked TTS') as chunks:
        for chunk in chunks:
            audio_file = f'{CACHE_DIR}/{service}_{model}_{voice}_{hashlib.md5(chunk.encode("utf-8")).hexdigest()}.mp3'
            if not os.path.exists(audio_file):
                with client.audio.speech.with_streaming_response.create(
                    model=model,
                    voice=voice,
                    input=chunk,
                ) as response:
                    response.stream_to_file(audio_file)

            outputs.append(audio_file)
            print('.', end='')

    joined = None
    with click.progressbar(outputs, label='Processing audio files') as output_files:
        for file in output_files:
            segment = AudioSegment.from_mp3(file)
            if joined is None:
                joined = segment
            else:
                joined += segment

    print('Finalizing...')
    joined.export('./tts_result.mp3', format='mp3')


if __name__ == '__main__':
    run_tts()
