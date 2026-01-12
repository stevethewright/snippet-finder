import logging
import os
from pathlib import Path
import faster_whisper
from google import genai

logger = logging.getLogger(__name__)


def is_gemini_key_set() -> bool:
    return os.getenv("GEMINI_API_KEY") is not None


def generate_transcript(
    audio_file: Path,
    model_size: str = "base",
    device: str = "auto",
    compute_type: str = "default",
):
    logger.debug(
        f"generate_transcript called. Parameters: audio_file={audio_file}, model_size={model_size}, device={device}, compute_type={compute_type}"
    )
    if not audio_file.is_file():
        logger.error("Could not transcribe. Provided path is not a file.")
        raise Exception("Provided path is not a file.")
    model = faster_whisper.WhisperModel(
        model_size, device=device, compute_type=compute_type
    )
    segments, info = model.transcribe(str(audio_file))
    logger.debug(f"generate_transcript complete. Returning: {segments, info}")
    return segments, info


def generate_key_points(segments):
    logger.debug(f"generate_key_points started. Parameters: {segments}")
    if not is_gemini_key_set():
        logger.error("Failed to start generating key points, no API key has been set.")
        raise Exception("Please provide GEMINI_API_KEY")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    full_transcript = ""
    for segment in segments:
        full_transcript += f'{{ "start": "{segment.start}", "end": "{segment.end}", "text": "{segment.text}" }}\n'
    input = f"""
    You are a JSON generator.

    Your task is to read a provided transcript in the form of a JSON array. Each segment has the following structure:
    {{
        "start": 0.0,
        "end": 5.0,
        "text": "Hello there, my name is John Smith."
    }}

    From this transcript, select 3-5 key points.

    Rules (STRICT):
    - Output MUST be valid JSON.
    - Output MUST be a single JSON array.
    - Output MUST contain ONLY JSON - no explanations, no comments, no markdown, no extra text.
    - Do NOT modify the original timestamps or text.
    - Each item must be copied verbatim from the input transcript.
    - Each item must represent an impactful, social-media-friendly takeaway.
    - Each item should be concise (1-2 sentences max).
    - If you cannot comply, return an empty JSON array: [].

    Required output format:
    [
        {{
            "start": number,
            "end": number,
            "text": string
        }}
    ]

    Here is the transcript to process:
    {full_transcript}
    """

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=input)

    logger.debug(f"generate_key_points complete. Returning: {response.text}")
    return response.text
