from pathlib import Path
from typing import Optional
import signal
import sys
from .vosk_transcriber import VoskTranscriber

class MeetingTranscriber:
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """Initialize transcription model with Vosk."""
        print("🎙️ Initializing Vosk Transcriber...")
        self.transcriber = VoskTranscriber()

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio using Vosk."""
        try:
            print(f"🎙️ Transcribing audio: {audio_path}")
            transcript = self.transcriber.transcribe(str(audio_path))
            print(f"✅ Transcription complete: {len(transcript)} characters")
            return transcript
        except Exception as e:
            print(f"❌ [red]Transcription failed: {type(e).__name__}: {e}[/red]")
            return ""