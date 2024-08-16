import nltk

from typing import Optional
from pydub import AudioSegment

from joinery.api.base import BaseTtsApi


class JoinOp:
    # This whole thing is kind of a kludge to allow reuse as a library while exposing the
    # methods to the CLI script in a way that makes it easy to generate progress bars.

    def __init__(self, text: str, api: BaseTtsApi):
        self.text = text
        self.api = api
        self._chunks = [[]]
        self._chunk_iter = 0

        self._audio_chunks = []

    def process_to_file(self, file_path):
        chunks = self.chunk_all()
        audio = None
        for chunk in chunks:
            result = self.run_tts(chunk)
            audio = self.join_audio(result, append_to=audio)
        audio.export(file_path)

    def chunk_all(self):
        for sent in self.tokenize():
            self.add_to_chunks(sent)
        return self.chunked_text()

    def tokenize(self) -> list[str]:
        self.sentences = nltk.sent_tokenize(self.text)
        return self.sentences

    def add_to_chunks(self, sentence: str):
        if (
            sum(map(len, self._chunks[self._chunk_iter]))
            + len(
                self._chunks[self._chunk_iter]
            )  # Account for re-adding spaces after each sentence
            + len(sentence)
            < 4096
        ):
            self._chunks[self._chunk_iter].append(sentence)
        else:
            self._chunk_iter += 1
            self._chunks.append(
                [sentence]
            )  # Will fail for sentences > 4096 chars, do we care?

    def chunked_text(self):
        return [" ".join(a) for a in self._chunks]

    def run_tts(self, chunk):
        return self.api.process_to_file(chunk)

    def join_audio(
        self, file_path, append_to: Optional[AudioSegment] = None
    ) -> AudioSegment:
        segment = AudioSegment.from_mp3(file_path)
        if append_to is None:
            append_to = segment
        else:
            append_to += segment

        return append_to
