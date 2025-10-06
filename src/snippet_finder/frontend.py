import os
from pathlib import Path
import threading
import tkinter
from tkinter import filedialog
from tkinter import ttk

from faster_whisper import available_models

from snippet_finder.backend import generate_transcript, generate_key_points

class SnippetFinder():
    def __init__(self, root: tkinter.Tk):
        self.root = root
        self.root.title("Snippet Finder")
        self.root.geometry("600x600")

        self.available_models = available_models()
        self.devices = ["auto", "cpu", "cuda"]
        self.compute_types = ['default', 'int8', 'float16', 'float32']

        # Whisper
        self.model_section_label = tkinter.Label(root, text="Whisper Options")
        self.model_section_label.grid(row=0, column=0)

        self.whisper_opt_frame = tkinter.Frame(self.root)
        self.whisper_opt_frame.grid(row=1, column=0)
        self.selected_model_label = tkinter.Label(self.whisper_opt_frame, text="Selected model:")
        self.selected_model_label.grid(row=0, column=0)
        self.model_combobox = ttk.Combobox(self.whisper_opt_frame, values=self.available_models)
        self.model_combobox.set("base")
        self.model_combobox.grid(row=0, column=1)
        self.selected_device_label = tkinter.Label(self.whisper_opt_frame, text="Selected device:")
        self.selected_device_label.grid(row=1, column=0)
        self.device_combobox = ttk.Combobox(self.whisper_opt_frame, values=self.devices)
        self.device_combobox.set("auto")
        self.device_combobox.grid(row=1, column=1)
        self.selected_compute_type_label = tkinter.Label(self.whisper_opt_frame, text="Selected Compute Type:")
        self.selected_compute_type_label.grid(row=2, column=0)
        self.compute_type_combobox = ttk.Combobox(self.whisper_opt_frame, values=self.compute_types)
        self.compute_type_combobox.set("default")
        self.compute_type_combobox.grid(row=2, column=1)

        # File selection
        self.file_select_frame = tkinter.Frame(self.root)
        self.file_select_frame.grid(row=2, column=0)
        self.chosen_file_label = tkinter.Label(self.file_select_frame, text="Selected audio file:")
        self.chosen_file_label.grid(row=0, column=0)
        self.selected_file_label = tkinter.Label(self.file_select_frame, text="No file selected.")
        self.selected_file_label.grid(row=0, column=1)
        self.file_select_button = tkinter.Button(self.file_select_frame, text="Select File", command=self.select_file)
        self.file_select_button.grid(row=0, column=2)

        # Fetch Snippets
        self.fetch_snippets_frame = tkinter.Frame(self.root)
        self.fetch_snippets_frame.grid(row=3, column=0)
        self.fetch_snippets_button = tkinter.Button(self.fetch_snippets_frame, text="Fetch Snippets", command=self.start_transcribe_and_analyse)
        self.fetch_snippets_button.grid(row=0, column=0)


    def select_file(self):
        # Open file dialog and allow the user to select a file
        self.file_path = filedialog.askopenfilename(title="Select a file")
        
        if self.file_path:
            # Display the file path in the label
            self.selected_file_label.config(text=os.path.basename(self.file_path))

    def transcribe_and_analyse(self):
        self.root.config(cursor="watch")
        segments, _ = generate_transcript(Path(self.file_path), self.model_combobox.get(), self.device_combobox.get(), self.compute_type_combobox.get())
        key_points = generate_key_points(segments)
        if key_points:
            with open("output.txt", "w") as file:
                file.write(key_points)
        self.root.config(cursor="arrow")

    def start_transcribe_and_analyse(self):
        task_thread = threading.Thread(target=self.transcribe_and_analyse)
        task_thread.start()

    def run(self):
        self.root.mainloop()
