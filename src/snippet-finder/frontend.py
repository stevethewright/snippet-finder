import tkinter
from tkinter import filedialog
from tkinter import scrolledtext

class SnippetFinder():
    def __init__(self, root: tkinter.Tk):
        self.root = root
        self.root.title("Snippet Finder")
        self.root.geometry("600x600")

        # File selection
        self.chosen_file_label = tkinter.Label(root, text="No file selected")
        self.chosen_file_label.pack(pady=20)
        self.file_select_button = tkinter.Button(root, text="Select File", command=self.select_file)
        self.file_select_button.pack()

        # Run
        self.transcribe_analyse_button = tkinter.Button(root, text="Transcribe & Analyse", command=self.transcribe_and_analyse)
        self.transcribe_analyse_button.pack()

        # Results
        self.results_title = tkinter.Label(root, text="Results")
        self.results_title.pack()
        self.results_widget = scrolledtext.ScrolledText(root, wrap=tkinter.WORD, width=70, height=15)
        self.results_widget.insert(tkinter.END, "No results")
        self.results_widget.pack(padx=10, pady=10)


    def select_file(self):
        # Open file dialog and allow the user to select a file
        file_path = filedialog.askopenfilename(title="Select a file")
        
        if file_path:
            # Display the file path in the label
            self.chosen_file_label.config(text=f"File selected: {file_path}")

    def transcribe_and_analyse(self):
        # segments, info = generate_transcript(Path(argv[1]))
        # generate_key_points(segments)
        transcript = "this is the transcript"
        key_points = "key points"
        self.results_widget.delete(1.0, tkinter.END)
        self.results_widget.insert(tkinter.END, key_points)

    def run(self):
        self.root.mainloop()
