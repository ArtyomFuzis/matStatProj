# python
import tkinter as tk
from tkinter import ttk
import pandas as pd


from Windows.SystemParamsShowWindow import SystemParamsShowWindow, AnswerType
from solver import estimate_system
from utils import calculate_msq, save_into_file


class EquationShowWindow:
    def __init__(self, parent, equations, reses_df):
        self.active_rows = set()
        self.window = tk.Toplevel(parent)
        self.window.geometry("600x400")
        self.window.title("Результат системы статистических уравнений")
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.equations = equations
        self.reses_df = reses_df
        self.load_selections_frames()
        self.close_btn = ttk.Button(self.window, text="Закрыть", command=self.close, width=50)
        self.close_btn.pack(anchor=tk.S, padx=10, pady=10)
        self.show_equations()


    def show_equations(self):
        grid_row = 0
        for el in self.equations:
            txt=f"{el[0]} = {round(el[1][0][1], 4)}"
            for i in range(1,len(el[1])):
                txt+=f" + {round(el[1][i][1], 4)} {el[1][i][0]}"
            cur_lbl = ttk.Entry(self.main_frame, font=('Arial', 12, 'bold'))
            cur_lbl.grid(row=grid_row, column=0, sticky=tk.NSEW, pady=10, columnspan=5)
            cur_lbl.insert(0, txt)
            cur_lbl.config(state='readonly')
            grid_row += 1

    def load_selections_frames(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        frame = tk.Frame(self.window)
        frame.pack(expand=True, fill=tk.BOTH)
        tree = ttk.Treeview(frame)
        tree["columns"] = list(self.reses_df.columns)
        tree["show"] = "headings"
        for col in self.reses_df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.W)
        for index, row in self.reses_df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.tag_configure('row_height', font=('TkDefaultFont', 14))
        tree.pack(fill=tk.BOTH, expand=True)

    def show(self):
        self.window.grab_set()
        self.window.wait_window()

    def close(self):
        self.window.destroy()


