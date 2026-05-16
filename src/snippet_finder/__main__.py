import logging
from logging.handlers import RotatingFileHandler
import os
import sys

if sys.platform == "darwin" and getattr(sys, "frozen", False):
    # When frozen with PyInstaller, help Qt find itself
    # without relying on CFBundleGetMainBundle()
    bundle_dir = os.path.dirname(os.path.dirname(sys.executable))
    frameworks = os.path.join(bundle_dir, "Frameworks")

    os.environ["QT_PLUGIN_PATH"] = os.path.join(frameworks, "PyQt6", "Qt6", "plugins")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
        frameworks, "PyQt6", "Qt6", "plugins", "platforms"
    )
    os.environ["DYLD_FRAMEWORK_PATH"] = frameworks
    os.environ["DYLD_LIBRARY_PATH"] = frameworks

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
