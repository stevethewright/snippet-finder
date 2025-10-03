from pathlib import Path
from sys import argv
from .backend import generate_key_points, generate_transcript

if __name__ == "__main__":
    segments, info = generate_transcript(Path(argv[1]))
    print(generate_key_points(segments))
    pass