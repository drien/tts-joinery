import os

from openai import OpenAI
from pathlib import Path
from typing import Optional

from joinery.api.base import BaseTtsApi
from joinery.exceptions import MissingConfigError


class OpenAIApi(BaseTtsApi):
    service = "openai"

    def __init__(self, *args, api_key: Optional[str] = None, **kwargs):
        if not api_key and not os.environ.get("OPENAI_API_KEY"):
            raise MissingConfigError(
                "OpenAI API adapter expects an API key argument or OPENAI_API_KEY environment variable"
            )
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        super().__init__(*args, **kwargs)

    def process_to_file(self, text: str) -> Path:
        file_path = self.get_file_path(text)
        if not self.caching_enabled or not file_path.exists():
            with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
            ) as response:
                response.stream_to_file(file_path)

        return file_path
