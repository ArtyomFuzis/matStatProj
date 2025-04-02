import tkinter as tk
from tkinter import ttk

from Windows.OpenWindow import OpenWindow


class MainWindow:

    def __init__(self):
        self.window  = tk.Tk()
        self.window.geometry("800x800")
        self.window.resizable(False, False)
        self.window.title("StatApp")
        self.menu_pane = tk.Menu(self.window)
        self.file_menu = tk.Menu(self.window, tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.file_menu_open)
        self.file_menu.add_command(label="Закрыть")
        self.file_menu.add_command(label="Выход")
        self.menu_pane.add_cascade(label="Файл", menu=self.file_menu)
        self.window.config(menu=self.menu_pane)

    def file_menu_open(self):
        ow = OpenWindow()
        res = ow.show()
        print(res)

    def show(self):
        self.window.mainloop()