from pathlib import Path
from sys import argv
import tkinter

from dotenv import load_dotenv
from .backend import generate_key_points, generate_transcript
from .frontend import SnippetFinder

if __name__ == "__main__":
    load_dotenv()
    # segments, info = generate_transcript(Path(argv[1]))
    # print(generate_key_points(segments))
    root = tkinter.Tk()
    app = SnippetFinder(root)
    app.run()
