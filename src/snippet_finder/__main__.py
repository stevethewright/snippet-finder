import sys

from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from snippet_finder.frontend import SnippetFinder

if __name__ == "__main__":
    load_dotenv()
    app = QApplication(sys.argv)
    window = SnippetFinder()
    window.show()
    sys.exit(app.exec())
