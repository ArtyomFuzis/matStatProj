# python
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning, showinfo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Windows.EquationShowWindow import EquationShowWindow
from Windows.SystemParamsShowWindow import SystemParamsShowWindow, AnswerType
from solver import estimate_system
from utils import calculate_msq, save_into_file


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
        self.components = {(0, 0): []}
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
                        if (i, y) in self.equations:
                            del self.equations[(i, y)]
                        i += 1
                    self.active_rows.remove(y)
                else:
                    if (x + 1, y) not in self.equations:
                        self.components[(x + 1, y)] = []
                        lbl = ttk.Label(self.main_frame, text="=")
                        lbl.grid(column=x + 1, row=y)
                        self.components[(x + 1, y)].append(lbl)
                        self.place_variable_select(x + 1, y)
                    if (x, y + 1) not in self.equations:
                        self.components[(0, y + 1)] = []
                        self.place_y_select(y + 1)

                    self.active_rows.add(y)
            else:
                if var == "VAR":
                    i = x + 1
                    while (i, y) in self.components:
                        for el in self.components[(i, y)]:
                            el.grid_forget()
                        if (i, y) in self.equations:
                            del self.equations[(i, y)]
                        i += 1
                elif (x + 1, y) not in self.equations:
                    self.components[(x + 1, y)] = []
                    lbl = ttk.Label(self.main_frame, text=f"+ {let(y)}_{x}" if x != 1 else f"{let(y)}_0+{let(y)}_1")
                    lbl.grid(column=2 * x, row=y)
                    self.components[(x + 1, y)].append(lbl)
                    self.place_variable_select(x + 1, y)
            self.equations[(x, y)] = var

        return changed

    def place_variable_select(self, x, y):
        variable = tk.StringVar(self.window)
        cols = []
        for col in self.df.columns:
            cols.append(col)
            cols.append("@" + col)
        w = ttk.OptionMenu(self.main_frame, variable, "VAR", *cols, "VAR", command=self.changer(x, y))
        w.grid(column=2 * x + 1, row=y)
        self.components[(x, y)].append(w)

    def place_y_select(self, y):
        variable = tk.StringVar(self.window)
        w = ttk.OptionMenu(self.main_frame, variable, "VAR", *self.df.columns, "VAR", command=self.changer(0, y))
        w.grid(column=0, row=y)
        self.components[(0, y)].append(w)

    def show(self):
        self.window.wait_window()

    def calculate(self):
        print("-----------------CALC_STARTED-----------------")
        used_var = set()
        for act_row in self.active_rows:
            used_var.add(self.equations[(0, act_row)])
        if (0, 0) not in self.equations or self.equations[(0, 0)] == 'VAR':
            showwarning("Ошибка", "Не выбрано ни одно уравнение!")
            self.window.focus_set()
        elif len(used_var) != len(self.active_rows):
            showwarning("Ошибка", "Какая-то эндогенная переменная повторяется в левой части системы!")
            self.window.focus_set()
        else:
            has_lag = False
            all_rows = set()
            for row in self.active_rows:
                i = 1
                cur_row = set()
                while (i, row) in self.equations:
                    if self.equations[(i, row)] != "VAR" and self.equations[(i, row)] not in used_var:
                        if self.equations[(i, row)][0] == "@":
                            has_lag = True
                        if self.equations[(i, row)] in cur_row:
                            showwarning("Ошибка", f"В строке {row + 1} найдены повторяющиеся переменные")
                            self.window.focus_set()
                            return
                        cur_row.add(self.equations[(i, row)])
                        all_rows.add(self.equations[(i, row)])
                    elif self.equations[(i, row)] in used_var:
                        if self.equations[(i, row)] == self.equations[(0, row)]:
                            showwarning("Ошибка", f"В строке {row + 1} переменная зависит сама от себя")
                            self.window.focus_set()
                            return
                    i += 1
            print(self.equations)
            print(all_rows)

            params_for_rows = {}
            for row in self.active_rows:
                i = 1
                H = 1 # в начале строки точно одна эндогенная переменная
                D = len(all_rows) # общее кол-во экзогенных переменных
                while (i, row) in self.equations:
                    if self.equations[(i, row)] == "VAR":
                        pass
                    elif self.equations[(i, row)] not in used_var:
                        D -= 1
                    else:
                        H += 1
                    i += 1
                print("H: ", H, " D: ", D)
                params_for_rows[row+1] = (D,H)

            res = SystemParamsShowWindow(self.window, params_for_rows, len(all_rows), len(used_var)).show()
            if res == AnswerType.Return:
                return

            df_shifted = pd.DataFrame()
            for col in self.df.columns:
                df_shifted["@" + col] = self.df[[col]].shift(1)
            cur_df = pd.concat([self.df, df_shifted], axis=1)
            if has_lag:
                cur_df = cur_df.iloc[1:]
            print("-----------------cur_df-----------------\n", cur_df)

            n = cur_df.shape[0]

            z = []
            masks = []
            y = []
            y_titles = []
            z_titles = []
            for row in self.active_rows:
                if not self.equations[(0, row)] == "VAR":
                    y_titles.append(self.equations[(0, row)])
                    y.append(cur_df[y_titles[-1]])

            for row in self.active_rows:
                i = 1
                cur_mask = [True]
                cur_z_titles = [None]
                cur_z = [np.ones(n)]
                while (i, row) in self.equations:
                    if not self.equations[(i, row)] == "VAR":
                        cur_mask.append(self.equations[(i, row)] in used_var)
                        cur_z_titles.append(self.equations[(i, row)])
                        cur_z.append(cur_df[cur_z_titles[-1]])
                    i += 1
                masks.append(cur_mask)
                z.append(np.column_stack(cur_z))
                z_titles.append(cur_z_titles)
            x_matrix = np.column_stack(list(map(lambda x: cur_df[x], set([
                self.equations[(i, row)] for (i, row) in self.equations if
                self.equations[(i, row)] != "VAR" and self.equations[(i, row)] not in used_var
            ]))))
            #print(z)
            #print(masks)
            #print(y)
            #print(x_matrix)
            equations = [(y[i], z[i],masks[i]) for i in range(len(y))]

            coefficients = estimate_system(equations, x_matrix, use_log_transform=False)
            #print(coefficients)
            equation_with_coeffs = [
                (y_titles[i], [
                    (z_titles[i][j], coefficients[i][0][j]) for j in range(len(z_titles[i]))
                ]) for i in range(len(y_titles))
            ]
            print("-----------------equations-----------------\n", equation_with_coeffs)

            reses = [
                np.dot(z[i], coefficients[i][0]) for i in range(len(y))
            ]
            print("-----------------reses-----------------\n", reses)
            res_df = pd.DataFrame()
            for i in range(len(y_titles)):
                res_df[y_titles[i]] = reses[i]
                res_df[y_titles[i]+" (истинное)"] = cur_df[y_titles[i]]
            show_window = EquationShowWindow(self.window, equation_with_coeffs,res_df)
            show_window.show()



            for i in range(len(y)):
                res_df = pd.DataFrame({'Полученные значения':reses[i], 'Настоящие значения':y[i]})
                res_df.plot(title=y_titles[i])

            plt.show()


