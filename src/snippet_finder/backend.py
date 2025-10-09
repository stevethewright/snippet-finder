import os
from pathlib import Path
import faster_whisper
from google import genai


def is_gemini_key_set() -> bool:
    return os.getenv("GEMINI_API_KEY") is not None


def generate_transcript(
    audio_file: Path,
    model_size: str = "base",
    device: str = "auto",
    compute_type: str = "default",
):
    if not audio_file.is_file():
        raise Exception("Provided path is not a file.")
    model = faster_whisper.WhisperModel(
        model_size, device=device, compute_type=compute_type
    )
    segments, info = model.transcribe(str(audio_file))
    return segments, info


def generate_key_points(segments):
    # Check for API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        raise Exception("Please provide GEMINI_API_KEY")

    full_transcript = ""
    for segment in segments:
        full_transcript += f'{{ "start": "{segment.start}", "end": "{segment.end}", "text": "{segment.text}" }}\n'
    # input=f"""You are a helpful assistant and will determine 3 - 5 key points from this audio transcript that could be used for social media. The data includes timestamps. Please include the timestamps of the best audio snippets in your response. Here is the transcript: {full_transcript}"
    input = f"""
    Your task is to read a provided transcript in the form of a JSON object, where each segment contains a start timestamp, end timestamp, and text content. Here's the structure of each object:
    {{
        "start": 0.0,
        "end": 5.0,
        "text": "Hello there, my name is John Smith."
    }}

    You will process this JSON transcript and return 3-5 key points. Each point should:

        1. Not change the original data - Keep the timestamps and the text intact.
        2. Be concise and suitable for social media - Focus on the most impactful, engaging takeaways that would resonate with a broad audience.
        3. Include the timestamp(s) - Each point should be tied to its respective timestamp range.
        4. Be clear and direct - Aim for punchy, attention-grabbing summaries with 1-2 sentences per point.
    
    Example of output format:
    [
        {{
            "start": 0.0,
            "end": 5.0,
            "text": "Hello there, my name is John Smith."
        }},
        {{
            "start": 10.0,
            "end": 15.0,
            "text": "I believe in the power of education to change lives."
        }}
    ]

    The goal is to make these points short, impactful, and easily shareable on platforms like Facebook and Instagram. Here is the transcript for processing:

    {full_transcript}
    """

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=input)

    return response.text
