from pathlib import Path
from sys import argv
from .backend import generate_transcript

if __name__ == "__main__":
    print(generate_transcript(Path(argv[1])))
    pass