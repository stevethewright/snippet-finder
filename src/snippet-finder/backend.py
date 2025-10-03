from pathlib import Path
import faster_whisper

def generate_transcript(file: Path):
    model = faster_whisper.WhisperModel("base")
    segments, info = model.transcribe(str(file))
    return segments, info
