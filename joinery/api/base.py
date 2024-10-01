import hashlib
import os

from pathlib import Path
from platformdirs import user_data_dir


class BaseTtsApi:
    service: str = None

    def __init__(self, model='tts-1', voice='alloy', caching_enabled=True):
        self.caching_enabled = caching_enabled
        self.model = model
        self.voice = voice

        self.CACHE_DIR = user_data_dir("tts_joinery", "com.drien")
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def get_file_path(self, text: str) -> Path:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return Path(
            f"{self.CACHE_DIR}/{self.service}_{self.model}_{self.voice}_{text_hash}.mp3"
        )

    def process_to_file(self, text: str) -> Path:
        raise NotImplementedError
