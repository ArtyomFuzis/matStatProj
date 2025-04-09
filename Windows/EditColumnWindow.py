import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import re
from tkinter.messagebox import askyesnocancel, showwarning

def get_validate_columns_names():
    columns_params_pattern = re.compile(r"^[a-zA-Zа-яёА-Я_Ё1-9]+$")

    def validate_columns(new_value):
        if new_value == "":
            return True
        return re.match(columns_params_pattern, new_value) is not None

    return validate_columns


class EditColumnWindow:

    def __init__(self, df, col):
        self.df = df
        self.col = col
        self.window = tk.Toplevel()
        self.window.geometry("200x120")
        self.window.resizable(False, False)
        self.window.title("Что вы хотите сделать?")
        validate_name= self.window.register(get_validate_columns_names())
        self.delete_btn = ttk.Button(self.window, text="Удалить", command=self.delete)
        self.delete_btn.pack(anchor=tk.N, pady=(2, 2), fill='x', padx=(5, 5))
        self.clone_btn = ttk.Button(self.window, text="Клонировать", command=self.clone)
        self.clone_btn.pack(anchor=tk.N, pady=(2, 2), fill='x', padx=(5, 5))
        self.rename_entry = ttk.Entry(self.window, validatecommand=(validate_name, '%P'), validate="key", justify="center")
        self.rename_entry.pack(anchor=tk.N, pady=(2, 2), fill='x', padx=(5, 5))
        self.rename_entry.insert(0, self.col)
        self.rename_btn = ttk.Button(self.window, text="Переименовать", command=self.rename)
        self.rename_btn.pack(anchor=tk.N, pady=(2, 2), fill='x', padx=(5, 5))

    def delete(self):
        self.window.destroy()
        res = askyesnocancel(title="Подтверждение", message=f"Вы уверены что хотите удалить '{self.col}'?\n")
        if res:
            self.df.drop(self.col, axis=1, inplace=True)
            self.window.destroy()


    def clone(self):
        self.df[self.col+"_"] = self.df[self.col]
        self.window.destroy()

    def rename(self):
        print("called")
        self.df.rename({self.col:self.rename_entry.get()}, axis=1, inplace=True)
        self.window.destroy()

    def show(self):
        self.window.grab_set()
        self.window.wait_window()
        return self.df
