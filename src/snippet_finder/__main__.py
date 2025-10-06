import tkinter

from dotenv import load_dotenv
from snippet_finder.frontend import SnippetFinder

if __name__ == "__main__":
    load_dotenv()
    root = tkinter.Tk()
    app = SnippetFinder(root)
    app.run()
