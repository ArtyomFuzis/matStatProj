# python
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

import pandas as pd

from Windows.EditColumnWindow import EditColumnWindow


def validate_koeff(new_value):
    if new_value == "":
        return True
    try:
        value = float(new_value)
        return True
    except ValueError:
        return False
class ModelVariablesWindow:
    def __init__(self, parent, data, ind, accumulated_results=None):
        self.col_num = 1 if accumulated_results is None else len(accumulated_results.columns)+1
        self.ind = ind
        self.tree = None
        self.parent = parent
        self.data = data
        self.window = tk.Toplevel(parent)
        self.window.geometry("600x400")
        self.window.title("Формирование модельных переменных")
        self.validate_koeff = self.window.register(validate_koeff)
        self.var_listbox = tk.Listbox(self.window, selectmode=tk.MULTIPLE)
        self.var_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.var_listbox.bind('<<ListboxSelect>>', self.onselect)
        self.update_listbox()
        self.coeff_frame = tk.Frame(self.window)
        self.coeff_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Списки для хранения виджетов меток и полей ввода коэффициентов
        self.koeffs = dict()

        #self.add_coeff_inputs()

        #self.add_btn = ttk.Button(self.window, text="Добавить переменную", command=self.add_coeff_inputs)
        #self.add_btn.pack(pady=5)
        #self.remove_btn = ttk.Button(self.window, text="Удалить переменную", command=self.remove_coeff_inputs)
        #self.remove_btn.pack(pady=5)

        self.calc_btn = ttk.Button(self.window, text="Рассчитать", command=self.calculate_model_variables)
        self.calc_btn.pack(pady=5)
        self.selected_fields = []
        self.accumulated_results = accumulated_results
        self.update_result_display()

    def onselect(self, evt):
        if self.selected_fields != self.var_listbox.curselection():
            for el in self.selected_fields:
                if el not in self.var_listbox.curselection():
                    self.selected_fields.remove(el)
                    self.remove_coeff_inputs(el)
            for el in self.var_listbox.curselection():
                if el not in self.selected_fields:
                    self.selected_fields.append(el)
                    self.add_coeff_inputs(el)

    def update_listbox(self):
        self.var_listbox.delete(0, tk.END)
        for col in self.data.columns:
            self.var_listbox.insert(tk.END, col)

    def add_coeff_inputs(self, field_ind):
        row = len(self.koeffs)
        label_name = ttk.Label(self.coeff_frame, text=self.var_listbox.get(field_ind))
        label_name.grid(row=row, column=0, padx=5, pady=5)
        alpha_label = ttk.Label(self.coeff_frame, text=f"\u03B1_{field_ind+1}:")
        alpha_label.grid(row=row, column=1, padx=5, pady=5)
        alpha_entry = ttk.Entry(self.coeff_frame, validatecommand=(self.validate_koeff, '%P'), validate="key")
        alpha_entry.grid(row=row, column=2, padx=5, pady=5)
        alpha_entry.insert(0, "1.0")


        beta_label = ttk.Label(self.coeff_frame, text=f"\u03B2_{field_ind+1}:")
        beta_label.grid(row=row, column=3, padx=5, pady=5)
        beta_entry = ttk.Entry(self.coeff_frame, validatecommand=(self.validate_koeff, '%P'), validate="key")
        beta_entry.grid(row=row, column=4, padx=5, pady=5)
        beta_entry.insert(0, "1.0")
        self.koeffs[field_ind]=(label_name,(alpha_label, alpha_entry),(beta_label, beta_entry))

    def remove_coeff_inputs(self, field_ind):
        if field_ind in self.koeffs:
            alpha = self.koeffs.get(field_ind)[1]
            beta = self.koeffs.get(field_ind)[2]
            lbl = self.koeffs.get(field_ind)[0]
            alpha[0].destroy()
            alpha[1].destroy()
            beta[1].destroy()
            beta[0].destroy()
            lbl.destroy()
            self.koeffs.pop(field_ind)

    def calculate_model_variables(self):
        selected_vars = [i for i in self.var_listbox.curselection()]
        if not selected_vars:
            showerror("Ошибка", "Не выбрана не одна переменная!")
            self.window.focus_set()
            return
        alphas = {key: float(self.koeffs[key][1][1].get()) for key in self.koeffs}
        betas = {key: float(self.koeffs[key][2][1].get()) for key in self.koeffs}

        model_vars = pd.DataFrame()

        for i in selected_vars:
            numeric_data = pd.to_numeric(self.data[self.var_listbox.get(i)], errors='coerce').dropna()
            model_vars[f"X_{i}"] = alphas[i] * betas[i] * numeric_data

        # Суммирование строк
        summed = model_vars.sum(axis=1)

        # Формирование нового столбца с именем результата
        if self.accumulated_results is None:
            self.accumulated_results = pd.DataFrame()

        name = f"X_{self.col_num}" if len(selected_vars) > 1 else self.var_listbox.get(selected_vars[0])
        self.accumulated_results[name] = summed
        self.col_num += 1

        self.update_result_display()
        self.clear_select()

    def clear_select(self):
        self.var_listbox.selection_clear(0, tk.END)
        self.onselect(None)
        self.onselect(None)


    def update_result_display(self):
       def select_var(var):
           def select_item():
               edit_column = EditColumnWindow(self.accumulated_results, var)
               edit_column.show()
               self.update_result_display()
               self.window.focus_set()

           return select_item
       if self.tree:
           self.tree.destroy()
       self.tree = ttk.Treeview(self.window)
       self.tree["show"] = "headings"
       self.tree.pack(fill=tk.BOTH, expand=True)
       if self.accumulated_results is not None:
           self.tree['columns'] = self.accumulated_results.columns.tolist()
       else:
           self.tree['columns'] = []
       if self.accumulated_results is not None:
           for col in self.accumulated_results.columns:
               self.tree.heading(col, text=col, command=select_var(col))
               self.tree.column(col, anchor=tk.NW, width=100)
           for index, row in self.accumulated_results.iterrows():
               self.tree.insert("", "end", values=list(row))

    def show(self):
        self.window.wait_window()
        return self.ind, self.accumulated_results



