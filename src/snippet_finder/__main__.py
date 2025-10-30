import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from snippet_finder.frontend import SnippetFinder

logger = logging.getLogger("snippet_finder")


def setup_logging():
    LOG_FILE = "snippet_finder.log"
    LOG_FORMAT = "%(asctime)s [%(levelname)s] (%(threadName)s) %(name)s: %(message)s"
    LOG_LEVEL = int(os.getenv("LOG_LEVEL", logging.INFO))
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger.log(
        LOG_LEVEL,
        f"Logging initialised. Log level set to {logging.getLevelName(LOG_LEVEL)}.",
    )


def main():
    load_dotenv()
    setup_logging()
    logger.info("Starting...")
    app = QApplication(sys.argv)
    window = SnippetFinder()
    window.show()
    logger.info("Window created.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
