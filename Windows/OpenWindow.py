import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import re
from utils import shorten_string
from tkinter.messagebox import askyesnocancel, showwarning


def validate_spinbox(new_value):
    if new_value == "":
        return True
    try:
        value = int(new_value)
        return 1 <= value <= 999999999
    except ValueError:
        return False


def get_validate_columns():
    columns_params_pattern = re.compile(r"^(?:([A-Z]+|[A-Z]+:[A-Z]*),?)+$")

    def validate_columns(new_value):
        if new_value == "":
            return True
        return re.match(columns_params_pattern, new_value) is not None

    return validate_columns


class OpenWindow:
    def disable_sub(self):
        self.send_btn.configure(state='disabled')
        self.label_row_num.configure(state='disabled')
        self.label_row_start.configure(state='disabled')
        self.label_columns.configure(state='disabled')
        self.spin_row_start.configure(state='disabled')
        self.spin_row_n.configure(state='disabled')
        self.text_columns.configure(state='disabled')

    def enable_sub(self):
        self.send_btn.configure(state='enabled')
        self.label_row_num.configure(state='enabled')
        self.label_row_start.configure(state='enabled')
        self.label_columns.configure(state='enabled')
        self.spin_row_start.configure(state='enabled')
        self.spin_row_n.configure(state='enabled')
        self.text_columns.configure(state='enabled')

    def __init__(self):
        self.df = None
        self.filepath = None
        self.window = tk.Toplevel()
        self.window.geometry("440x480")
        self.window.resizable(False, False)
        self.window.title("Открыть")
        validate_spin = self.window.register(validate_spinbox)
        validate_cols = self.window.register(get_validate_columns())
        self.ctrl_frame = tk.Frame(self.window)
        self.ctrl_frame.pack(fill='both', expand=True)
        self.choose_btn = ttk.Button(self.ctrl_frame, text="Файл...", command=self.file_choose)
        self.choose_btn.configure(width=22)
        self.choose_btn.pack(anchor=tk.N, pady=(5, 10), fill='x', padx=(5, 5))
        self.label_row_start = ttk.Label(self.ctrl_frame, text="Номер строки начала данных:")
        self.label_row_start.pack(anchor=tk.NW, pady=(0, 5), padx=(5, 0))
        self.spin_row_start = ttk.Spinbox(self.ctrl_frame, from_=1, to=999999999, validate="key",
                                          validatecommand=(validate_spin, '%P'), )
        self.spin_row_start.set(1)
        self.spin_row_start.pack(anchor=tk.N, padx=(5, 0))
        self.label_row_num = ttk.Label(self.ctrl_frame, text="Количество строк данных (c заголовком):")
        self.label_row_num.pack(anchor=tk.NW, pady=(0, 5), padx=(5, 0))
        self.spin_row_n = ttk.Spinbox(self.ctrl_frame, from_=1, to=999999999, validate="key",
                                      validatecommand=(validate_spin, '%P'))
        self.spin_row_n.set(1)
        self.spin_row_n.pack(anchor=tk.N, padx=(5, 0))
        self.label_columns = ttk.Label(self.ctrl_frame, text="Столбцы (пример ввода: A:C,J):")
        self.label_columns.pack(anchor=tk.NW, pady=(0, 5), padx=(5, 0))
        self.text_columns = ttk.Entry(self.ctrl_frame, validate="key",
                                      validatecommand=(validate_cols, '%P'))
        self.text_columns.pack(anchor=tk.N)
        self.send_btn = ttk.Button(self.ctrl_frame, text="Открыть", command=self.file_to_pandas)
        self.send_btn.configure(width=22)
        self.send_btn.pack(anchor=tk.S, pady=(5, 5), fill='x', padx=(5, 5))
        self.disable_sub()
        self.label_err = ttk.Label(self.ctrl_frame, text="Ошибка", foreground="red")

    def show(self):
        self.window.grab_set()
        self.window.wait_window()
        return self.df

    def file_choose(self):
        self.filepath = filedialog.askopenfilename(defaultextension=".xlsx", filetypes=(("Файлы Excel", "*.xlsx"),))
        if self.filepath:
            filename = shorten_string(self.filepath.split("/")[-1], 20)
            self.choose_btn.configure(text=filename)
            self.enable_sub()

    def file_to_pandas(self):
        row_pre_start = int(self.spin_row_start.get()) - 1
        row_n = int(self.spin_row_n.get()) - 1
        try:
            df = pd.read_excel(self.filepath, skiprows=row_pre_start, nrows=row_n, usecols=self.text_columns.get())
            res = askyesnocancel(title="Подтверждение", message="Правильно ли считана таблица?\n" + str(df))
            if res:
                self.df = df
                self.window.destroy()
        except ValueError:
            self.disable_sub()
            self.choose_btn.configure(text="Файл...")
            self.filepath = None
            showwarning(message="Выбранный файл имеет некорректный формат", title="Ошибка")
