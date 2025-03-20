import glob
import hashlib
import os

from pathlib import Path
from platformdirs import user_data_dir


class BaseTtsApi:
    service: str = None

    def __init__(self, model="tts-1", voice="alloy", caching_enabled=True):
        self.caching_enabled = caching_enabled
        self.model = model
        self.voice = voice

        self.CACHE_DIR = user_data_dir("tts_joinery", "com.drien")
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def clear_cache(self):
        # Duplicated from cli.py where it has more verbose output
        files = glob.glob(f"{self.CACHE_DIR}/*")
        for f in files:
            os.remove(f)

    def get_file_path(self, text: str) -> Path:
        hash_content = text
        if (
            hasattr(self, "instructions")
            and self.instructions
            and self.model == "gpt-4o-mini-tts"
        ):
            hash_content = f"{text}|||{self.instructions}"
        text_hash = hashlib.md5(hash_content.encode("utf-8")).hexdigest()
        return Path(
            f"{self.CACHE_DIR}/{self.service}_{self.model}_{self.voice}_{text_hash}.mp3"
        )

    def process_to_file(self, text: str) -> Path:
        raise NotImplementedError
