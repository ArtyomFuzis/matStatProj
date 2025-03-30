import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class OpenWindow:

    def __init__(self):
        self.window = tk.Toplevel()
        self.window.geometry("300x300")
        self.window.resizable(False, False)
        self.window.title("Открыть")
        self.choose_btn = ttk.Button(self.window, text="Файл...", command=self.file_choose)
        self.choose_btn.pack()

    def show(self):
        self.window.grab_set()
        self.window.wait_window()

    def file_choose(self):
        file = filedialog.askopenfilename(defaultextension=".xlsx", filetypes=(("Файлы Excel", "*.xlsx"),))