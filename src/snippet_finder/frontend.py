import logging
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
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

        # Tabs
        tabs = QTabWidget()
        basic_tab = QWidget()
        advanced_tab = QWidget()

        self.available_models = available_models()
        self.devices = ["cpu"]  # TODO: Cuda is not supported.
        self.compute_types = ["default", "int8", "float16", "float32"]

        basic_layout = QVBoxLayout()
        advanced_layout = QVBoxLayout()

        # Whisper Options
        advanced_layout.addLayout(self._create_whisper_model_select())

        # File selection
        self.selected_file_label = self._create_file_select_label()
        basic_layout.addLayout(self._create_file_select(self.selected_file_label))
        advanced_layout.addLayout(self._create_file_select(self.selected_file_label))
        # TODO: can we share the file state instead of the label?

        # Output Options
        model_section_label = QLabel("Output Options")
        basic_layout.addWidget(model_section_label)
        advanced_layout.addWidget(model_section_label)

        basic_layout.addLayout(self._create_output_select())
        advanced_layout.addLayout(self._create_output_select())

        # Fetch Snippets
        basic_layout.addWidget(self._create_fetch_snippets_button())
        advanced_layout.addWidget(self._create_fetch_snippets_button())

        # Output Display
        model_section_label = QLabel("Output")
        basic_layout.addWidget(model_section_label)
        advanced_layout.addWidget(model_section_label)
        basic_layout.addWidget(self._create_output_display())
        advanced_layout.addWidget(self._create_output_display())

        # Transcript Display
        self.model_section_label = QLabel("Transcript")
        advanced_layout.addWidget(self.model_section_label)
        advanced_layout.addWidget(self._create_transcript_display())

        # Add tabs
        basic_tab.setLayout(basic_layout)
        advanced_tab.setLayout(advanced_layout)
        tabs.addTab(basic_tab, "Basic")
        tabs.addTab(advanced_tab, "Advanced")
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def _create_whisper_model_select(self) -> QGridLayout:
        whisper_layout = QGridLayout()
        model_section_label = QLabel("Whisper Options")
        whisper_layout.addWidget(model_section_label, 0, 0)
        whisper_layout.addWidget(QLabel("Selected model:"), 1, 0)
        model_combobox = QComboBox()
        model_combobox.addItems(self.available_models)
        model_combobox.setCurrentText("base")
        whisper_layout.addWidget(model_combobox, 1, 1)

        whisper_layout.addWidget(QLabel("Selected device:"), 2, 0)
        device_combobox = QComboBox()
        device_combobox.addItems(self.devices)
        device_combobox.setCurrentText("auto")
        whisper_layout.addWidget(device_combobox, 2, 1)

        whisper_layout.addWidget(QLabel("Selected Compute Type:"), 3, 0)
        compute_type_combobox = QComboBox()
        compute_type_combobox.addItems(self.compute_types)
        compute_type_combobox.setCurrentText("default")
        whisper_layout.addWidget(compute_type_combobox, 3, 1)
        return whisper_layout

    def _create_file_select_label(self) -> QLabel:
        return QLabel("No file selected.")

    def _create_file_select(self, selected_file_label: QLabel) -> QHBoxLayout:
        file_layout = QHBoxLayout()
        chosen_file_label = QLabel("Selected audio file:")
        file_layout.addWidget(chosen_file_label)
        file_layout.addWidget(selected_file_label)
        file_select_button = QPushButton("Select File")
        file_select_button.clicked.connect(
            lambda: self.select_file(selected_file_label)
        )
        file_layout.addWidget(file_select_button)
        return file_layout

    def _create_output_select(self) -> QHBoxLayout:
        target_file_layout = QHBoxLayout()
        chosen_target_file_label = QLabel("Selected target file:")
        target_file_layout.addWidget(chosen_target_file_label)
        selected_target_file_label = QLabel("No target file selected.")
        target_file_layout.addWidget(selected_target_file_label)
        target_file_select_button = QPushButton("Select File")
        target_file_select_button.clicked.connect(self.get_save_path)
        target_file_layout.addWidget(target_file_select_button)
        return target_file_layout

    def _create_fetch_snippets_button(self) -> QPushButton:
        fetch_snippets_button = QPushButton("Fetch Snippets")
        fetch_snippets_button.clicked.connect(self.transcribe_and_analyse)
        return fetch_snippets_button

    def _create_output_display(self) -> QPlainTextEdit:
        output_text_edit = QPlainTextEdit()
        output_text_edit.setReadOnly(True)
        output_text_edit.setPlainText("Fetch snippet to get a result.")
        return output_text_edit

    def _create_transcript_display(self) -> QPlainTextEdit:
        transcript_text_edit = QPlainTextEdit()
        transcript_text_edit.setReadOnly(True)
        transcript_text_edit.setPlainText("Fetch snippet to get a transcript.")
        return transcript_text_edit

    def select_file(self, selected_file_label: QLabel):
        logger.debug("select_file called.")
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select a file", "", "Audio Files (*.mp3 *.wav *.m4a);;All Files (*)"
        )
        logger.debug(f"File selected. file_path={file_path}.")
        if file_path:
            self.file_path = file_path
            selected_file_label.setText(os.path.basename(file_path))
        logger.debug("select_file complete.")

    def get_save_path(self):
        logger.debug("get_save_path called.")
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Target output file", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.target_file_path = file_path
            self.selected_target_file_label.setText(os.path.basename(file_path))
        logger.debug("get_save_path complete.")

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
            transcript = "".join(segment.text for segment in segments)
            self.transcript_text_edit.setPlainText(transcript.strip())
            key_points = generate_key_points(segments)
            logger.info("Key point analysis complete.")
            if key_points:
                result = self.parse_output(key_points)
                self.output_text_edit.setPlainText(result)
                if self.target_file_path:
                    logger.info(f"Saving to {self.target_file_path}")
                    with open(self.target_file_path, "w") as file:
                        file.write(result)
        except Exception as e:
            logger.error(f"Transcription/Analysis Failed. Error: {e}")
            QMessageBox.critical(self, "Transcription/Analysis Failed", str(e))
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        logger.debug("transcribe_and_analyse complete.")

    def parse_output(self, text: str) -> str:
        split_text = text.split("\n")
        if split_text[0] == "```json":
            text = "\n".join(split_text[1:-1])
        return text
