import tkinter as tk
from tkinter import ttk
import pandas as pd
from Windows.ModelVariablesWindow import open_model_variables_window
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
        self.tree = None
        self.current_df = None

        self.model_btn = ttk.Button(self.window, text="Формировать модельные переменные",
                                    command=self.open_model_variables)
        self.model_btn.pack(pady=10)

    def file_menu_open(self):
        ow = OpenWindow()
        res = ow.show()
        if res is not None:
            self.display_dataframe(res)

    def display_dataframe(self, df: pd.DataFrame):
        self.current_df = df
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)

        if self.tree:
            self.tree.destroy()
        self.tree = ttk.Treeview(self.window)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W)
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
        self.tree.tag_configure('row_height', font=('TkDefaultFont', 14))

    def open_model_variables(self):
        if self.current_df is not None:
            open_model_variables_window(self.window, self.current_df)
        else:
            tk.messagebox.showwarning(message="Сначала загрузите данные", title="Ошибка")

    def show(self):
        self.window.mainloop()