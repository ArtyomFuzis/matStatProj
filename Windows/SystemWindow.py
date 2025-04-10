# python
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning
import numpy as np
import pandas as pd

from Windows.EditColumnWindow import EditColumnWindow



class SystemWindow:
    def __init__(self, df: pd.DataFrame, parent):
        self.df = df
        self.active_rows = set()
        self.window = tk.Toplevel(parent)
        self.window.geometry("600x400")
        self.window.title("Система статистических уравнений")
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.equations = dict()
        self.components = {(0 ,0): []}
        self.place_y_select(0)
        self.calculate_btn = ttk.Button(self.window, text="Вычислить", command=self.calculate, width=50)
        self.calculate_btn.pack(anchor=tk.S, padx=10, pady=10)


    def changer(self, x, y):
        def let(y):
            return chr(ord('a') + y)
        def changed(var):
            if x == 0:
                if var == "VAR":
                    i = 1
                    while (i, y) in self.components:
                        for el in self.components[(i, y)]:
                            el.grid_forget()
                        if (i,y) in self.equations:
                            del self.equations[(i, y)]
                        i+=1
                    self.active_rows.remove(y)
                else:
                    if (x+1, y) not in self.equations:
                        self.components[(x+1, y)] = []
                        lbl = ttk.Label(self.main_frame,text="=")
                        lbl.grid(column=x+1, row=y)
                        self.components[(x + 1, y)].append(lbl)
                        self.place_variable_select(x+1, y)
                    if (x, y+1) not in self.equations:
                        self.components[(0, y+1)] = []
                        self.place_y_select(y + 1)

                    self.active_rows.add(y)
            else:
                if var == "VAR":
                    i = x+1
                    while (i, y) in self.components:
                        for el in self.components[(i, y)]:
                            el.grid_forget()
                        if (i,y) in self.equations:
                            del self.equations[(i, y)]
                        i+=1
                elif (x+1, y) not in self.equations:
                    self.components[(x + 1, y)] = []
                    lbl = ttk.Label(self.main_frame, text=f"+ {let(y)}_{x+1}" if x != 1 else f"{let(y)}_0+{let(y)}_1")
                    lbl.grid(column=2*x, row=y)
                    self.components[(x + 1, y)].append(lbl)
                    self.place_variable_select(x+1, y)
            self.equations[(x, y)] = var
        return changed

    def place_variable_select(self, x, y):
        variable = tk.StringVar(self.window)
        cols = []
        for col in self.df.columns:
            cols.append(col)
            cols.append("@"+col)
        w = ttk.OptionMenu(self.main_frame, variable, "VAR", *cols, "VAR", command=self.changer(x, y))
        w.grid(column=2*x+1, row=y)
        self.components[(x, y)].append(w)

    def place_y_select(self, y):
        variable = tk.StringVar(self.window)
        w = ttk.OptionMenu(self.main_frame, variable, "VAR", *self.df.columns, "VAR", command=self.changer(0, y))
        w.grid(column=0, row=y)
        self.components[(0, y)].append(w)

    def show(self):
        self.window.wait_window()

    def calculate(self):
        used_var = set()
        for act_row in self.active_rows:
            used_var.add(self.equations[(0,act_row)])
        if (0,0) not in self.equations:
            showwarning("Ошибка","Не выбрано ни одно уравнение!")
            self.window.focus_set()
        elif len(used_var) != len(self.active_rows):
            showwarning("Ошибка", "Какая-то эндогенная переменная повторяется в левой части системы!")
            self.window.focus_set()
        else:
            all_rows = set()
            for row in self.active_rows:
                i = 1
                cur_row = set()
                while (i, row) in self.equations:
                    if self.equations[(i,row)] != "VAR" and self.equations[(i,row)] not in used_var:
                        if self.equations[(i,row)] in cur_row:
                            showwarning("Ошибка", f"В строке {row+1} найдены повторяющиеся переменные")
                            self.window.focus_set()
                            return
                        cur_row.add(self.equations[(i,row)])
                        all_rows.add(self.equations[(i,row)])
                    i+= 1
            for row in self.active_rows:
                i = 1
                H = 1
                D = len(all_rows)
                while (i, row) in self.equations:
                    if self.equations[(i,row)] != "VAR" and self.equations[(i,row)] not in used_var:
                        D-=1
                    else:
                        H+= 1
                    i+= 1
                if H > D + 1:
                    showwarning("Ошибка", f"В строке {row + 1} неидентифицируемое уравнение")
                    self.window.focus_set()
                    return
            df_shifted = pd.DataFrame()
            for col in self.df.columns:
                df_shifted["@"+col] = self.df[[col]].shift(1)
            cur_df = pd.concat([self.df, df_shifted], axis=1)
            print(cur_df)
            matrix_X = np.hstack((np.ones((self.df.shape[0],1)), np.array(cur_df[list(all_rows)])))
            matrix_Y = np.array(cur_df[list(used_var)])
            print(matrix_X)
            print(matrix_Y)
            res = np.dot(np.dot(np.linalg.inv(np.dot(matrix_X.T, matrix_X)), matrix_X.T), matrix_Y)
            print(res)


