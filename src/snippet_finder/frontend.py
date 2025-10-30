import logging
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from faster_whisper import available_models

from snippet_finder.backend import (
    generate_transcript,
    generate_key_points,
    is_gemini_key_set,
)

logger = logging.getLogger(__name__)


class SnippetFinder(QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = None
        self.setWindowTitle("Snippet Finder")
        self.setGeometry(100, 100, 600, 150)

        self.available_models = available_models()
        self.devices = ["auto", "cpu", "cuda"]
        self.compute_types = ["default", "int8", "float16", "float32"]

        main_layout = QVBoxLayout()

        # Whisper Options
        self.model_section_label = QLabel("Whisper Options")
        main_layout.addWidget(self.model_section_label)

        whisper_layout = QGridLayout()
        whisper_layout.addWidget(QLabel("Selected model:"), 0, 0)
        self.model_combobox = QComboBox()
        self.model_combobox.addItems(self.available_models)
        self.model_combobox.setCurrentText("base")
        whisper_layout.addWidget(self.model_combobox, 0, 1)

        whisper_layout.addWidget(QLabel("Selected device:"), 1, 0)
        self.device_combobox = QComboBox()
        self.device_combobox.addItems(self.devices)
        self.device_combobox.setCurrentText("auto")
        whisper_layout.addWidget(self.device_combobox, 1, 1)

        whisper_layout.addWidget(QLabel("Selected Compute Type:"), 2, 0)
        self.compute_type_combobox = QComboBox()
        self.compute_type_combobox.addItems(self.compute_types)
        self.compute_type_combobox.setCurrentText("default")
        whisper_layout.addWidget(self.compute_type_combobox, 2, 1)

        main_layout.addLayout(whisper_layout)

        # File selection
        file_layout = QHBoxLayout()
        self.chosen_file_label = QLabel("Selected audio file:")
        file_layout.addWidget(self.chosen_file_label)
        self.selected_file_label = QLabel("No file selected.")
        file_layout.addWidget(self.selected_file_label)
        self.file_select_button = QPushButton("Select File")
        self.file_select_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_select_button)
        main_layout.addLayout(file_layout)

        # Fetch Snippets
        self.fetch_snippets_button = QPushButton("Fetch Snippets")
        self.fetch_snippets_button.clicked.connect(self.transcribe_and_analyse)
        main_layout.addWidget(self.fetch_snippets_button)

        self.setLayout(main_layout)

    def select_file(self):
        logger.debug("select_file called.")
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select a file", "", "Audio Files (*.mp3 *.wav *.m4a);;All Files (*)"
        )
        logger.debug(f"File selected. file_path={file_path}.")
        if file_path:
            self.file_path = file_path
            self.selected_file_label.setText(os.path.basename(file_path))
        logger.debug("select_file complete.")

    def transcribe_and_analyse(self):
        logger.debug("transcribe_and_analyse called.")
        self.setCursor(Qt.CursorShape.WaitCursor)

        if not is_gemini_key_set():
            logger.error(
                "Failed to start transcription and analysis, no API key has been set."
            )
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(
                self,
                "No API Key Found",
                "Environment variable GEMINI_API_KEY has not been set.",
            )
            return

        if self.file_path is None:
            logger.error(
                "Failed to start transcription and analysis, no file path has been set."
            )
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(
                self,
                "No File Provided",
                "Please select an audio file for transcripting.",
            )
            return
        try:
            logger.info("Generating transcript...")
            segments, _ = generate_transcript(
                Path(self.file_path),
                self.model_combobox.currentText(),
                self.device_combobox.currentText(),
                self.compute_type_combobox.currentText(),
            )
            logger.info("Transcription complete. Analysing key points...")
            key_points = generate_key_points(segments)
            if key_points:
                logger.info("Key point analysis complete. Saving to output.txt")
                with open("output.txt", "w") as file:
                    file.write(key_points)
        except Exception as e:
            logger.error(f"Transcription/Analysis Failed. Error: {e}")
            QMessageBox.critical(self, "Transcription/Analysis Failed", str(e))
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        logger.debug("transcribe_and_analyse complete.")
