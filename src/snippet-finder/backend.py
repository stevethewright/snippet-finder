import os
from pathlib import Path
import faster_whisper
from google import genai

def generate_transcript(file: Path):
    model = faster_whisper.WhisperModel("base")
    segments, info = model.transcribe(str(file))
    return segments, info

def generate_key_points(segments):
    full_transcript = ""
    for segment in segments:
        full_transcript += f'{{ "start": "{segment.start}", "end": "{segment.end}", "text": "{segment.text}" }}\n'
    input=f"You are a helpful assistant and will determine 3 - 5 key points from this audio transcript that could be used for social media. The data includes timestamps. Please include the timestamps of the best audio snippets in your response. Here is the transcript: {full_transcript}"
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY is None:
        raise Exception("Please provide GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)

    # TODO: Pass in API Key.
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=input
    )

    # Extract and return the response from the API
    return response.text
