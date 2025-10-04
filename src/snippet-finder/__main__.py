from pathlib import Path
from sys import argv

from dotenv import load_dotenv
from .backend import generate_key_points, generate_transcript

if __name__ == "__main__":
    load_dotenv()
    segments, info = generate_transcript(Path(argv[1]))
    print(generate_key_points(segments))
    pass