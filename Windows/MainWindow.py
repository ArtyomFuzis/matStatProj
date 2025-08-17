import tkinter as tk
from tkinter import ttk
import pandas as pd

from Windows.SystemWindow import SystemWindow
from Windows.ModelVariablesWindow import ModelVariablesWindow
from Windows.OpenWindow import OpenWindow
class MainWindow:

    def __init__(self, preloaded):
        self.window  = tk.Tk()
        self.window.geometry("800x800")
        self.window.resizable(True, False)
        self.window.title("StatApp")
        self.menu_pane = tk.Menu(self.window)
        self.file_menu = tk.Menu(self.window, tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.file_menu_open)
        self.menu_pane.add_cascade(label="Файл", menu=self.file_menu)
        self.window.config(menu=self.menu_pane)
        self.tree = None
        self.current_df = None
        self.note = ttk.Notebook()
        self.note.pack(expand=True, fill=tk.BOTH)
        self.frame_source = tk.Frame(self.note)
        self.frame_source.pack(expand=True, fill=tk.BOTH)
        self.dataframes = dict()
        self.note.add(self.frame_source, text="Исходные данные")
        self.model_btn = ttk.Button(self.frame_source, text="Формировать модельные переменные",
                                    command=self.open_model_variables)
        self.model_btn.pack(pady=10)
        self.display_dataframe(preloaded)
        self.frame_ind = 0

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
        self.tree = ttk.Treeview(self.frame_source)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W)
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
        self.tree.tag_configure('row_height', font=('TkDefaultFont', 14))

    def load_selections_frames(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        for item in self.note.winfo_children():
            if str(item) != str(self.frame_source):
                item.destroy()
        for key in self.dataframes:
            frame = tk.Frame(self.note)
            frame.pack(expand=True, fill=tk.BOTH)
            self.note.add(frame, text="Выборка "+str(key))
            tree = ttk.Treeview(frame)

            df = self.dataframes[key]
            model_btn = ttk.Button(frame, text="Редактировать модельные переменные",
                                   command=self.create_edit_model_variables_action(df))
            model_btn.pack(pady=10)
            system_btn = ttk.Button(frame, text="Создать систему",
                                   command=self.create_system(df))
            system_btn.pack(pady=10)
            tree["columns"] = list(df.columns)
            tree["show"] = "headings"
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, anchor=tk.W)
            for index, row in df.iterrows():
                tree.insert("", "end", values=list(row))
            tree.tag_configure('row_height', font=('TkDefaultFont', 14))
            tree.pack(fill=tk.BOTH, expand=True)

    def open_model_variables(self):
        if self.current_df is not None and len(self.current_df) != 0:
            self.frame_ind+=1
            res = ModelVariablesWindow(self.window, self.current_df, self.frame_ind).show()
            if res is not None and res[1] is not None:
                self.dataframes[res[0]] = res[1]
            self.load_selections_frames()
        else:
            tk.messagebox.showwarning(message="Сначала загрузите данные", title="Ошибка")
    def create_edit_model_variables_action(self, df):
        def edit_model_variables():
            ModelVariablesWindow(self.window, self.current_df, self.frame_ind, df).show()
            # if res is not None and res[1] is not None:
            #     self.dataframes[res[0]] = res[1]
            self.load_selections_frames()
        return edit_model_variables

    def show(self):
        self.window.mainloop()

    def create_system(self, df: pd.DataFrame):
        def system():
            SystemWindow(df, self.window).show()
        return system