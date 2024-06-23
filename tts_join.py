import click
import glob
import nltk
import os
import re

from openai import OpenAI
from pydub import AudioSegment

# Diffing by sentence to re-read??

@click.command()
@click.option('--voice', default='alloy')
@click.option('--service', default='openai')
def run_tts(voice, service):
    nltk.download('punkt')


    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    chunked_input = [[]]
    i = 0
    with open('draft.txt', 'r') as input_file:
        sentences = nltk.sent_tokenize(input_file.read())
        for sentence in sentences:
            if sum(map(len, chunked_input[i])) + len(chunked_input[i]) + len(sentence) < 4096:
                chunked_input[i].append(sentence)
            else:
                i += 1
                chunked_input.append([sentence]) # Will fail for sentences > 4096 chars

    chunked_input = [' '.join(a) for a in chunked_input]

    print(f'Preparing to run TTS in {len(chunked_input)} chunks...({list(map(len, chunked_input))})')

    for n, chunk in enumerate(chunked_input):
        print('.', end='')
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=chunk,
        )

        response.stream_to_file(f"output_segment_{n}.mp3")

    files = glob.glob('output_segment_*.mp3')
    joined = None
    for file in sorted(files):
        segment = AudioSegment.from_mp3(file)
        if joined is None:
            joined = segment
        else:
            joined += segment

    joined.export('tts_result.mp3', format='mp3')



if __name__ == '__main__':
    run_tts()
