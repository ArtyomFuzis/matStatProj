# Python
import tkinter as tk
from tkinter import ttk
import pandas as pd

class ModelVariablesWindow:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data
        self.window = tk.Toplevel(parent)
        self.window.geometry("600x400")
        self.window.title("Формирование модельных переменных")

        self.selection_mode = tk.StringVar(value="column")

        self.row_radio = ttk.Radiobutton(self.window, text="По строкам", variable=self.selection_mode, value="row")
        self.row_radio.pack(anchor=tk.W, padx=10, pady=5)
        self.column_radio = ttk.Radiobutton(self.window, text="По столбцам", variable=self.selection_mode, value="column")
        self.column_radio.pack(anchor=tk.W, padx=10, pady=5)

        self.var_listbox = tk.Listbox(self.window, selectmode=tk.MULTIPLE)
        self.var_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.update_listbox()

        self.coeff_frame = tk.Frame(self.window)
        self.coeff_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Списки для хранения виджетов меток и полей ввода коэффициентов
        self.alpha_labels = []
        self.alpha_entries = []
        self.beta_labels = []
        self.beta_entries = []

        self.add_coeff_inputs()

        # Кнопка для добавления новых переменных
        self.add_btn = ttk.Button(self.window, text="Добавить переменную", command=self.add_coeff_inputs)
        self.add_btn.pack(pady=5)
        # Кнопка для удаления последней переменной
        self.remove_btn = ttk.Button(self.window, text="Удалить переменную", command=self.remove_coeff_inputs)
        self.remove_btn.pack(pady=5)

        self.calc_btn = ttk.Button(self.window, text="Рассчитать", command=self.calculate_model_variables)
        self.calc_btn.pack(pady=5)

        self.result_text = tk.Text(self.window, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_listbox(self):
        self.var_listbox.delete(0, tk.END)
        if self.selection_mode.get() == "column":
            for col in self.data.columns:
                self.var_listbox.insert(tk.END, col)
        else:
            for index in self.data.index:
                self.var_listbox.insert(tk.END, index)

    def add_coeff_inputs(self):
        row = len(self.alpha_entries)
        alpha_label = ttk.Label(self.coeff_frame, text=f"\u03B1_{row+1}:")
        alpha_label.grid(row=row, column=0, padx=5, pady=5)
        alpha_entry = ttk.Entry(self.coeff_frame)
        alpha_entry.grid(row=row, column=1, padx=5, pady=5)
        self.alpha_labels.append(alpha_label)
        self.alpha_entries.append(alpha_entry)

        beta_label = ttk.Label(self.coeff_frame, text=f"\u03B2_{row+1}:")
        beta_label.grid(row=row, column=2, padx=5, pady=5)
        beta_entry = ttk.Entry(self.coeff_frame)
        beta_entry.grid(row=row, column=3, padx=5, pady=5)
        self.beta_labels.append(beta_label)
        self.beta_entries.append(beta_entry)

    def remove_coeff_inputs(self):
        if self.alpha_entries:
            # Удаляем виджеты последней добавленной строки
            last_alpha_label = self.alpha_labels.pop()
            last_alpha_entry = self.alpha_entries.pop()
            last_beta_label = self.beta_labels.pop()
            last_beta_entry = self.beta_entries.pop()
            last_alpha_label.destroy()
            last_alpha_entry.destroy()
            last_beta_label.destroy()
            last_beta_entry.destroy()

    def calculate_model_variables(self):
        selected_vars = [self.var_listbox.get(i) for i in self.var_listbox.curselection()]
        alphas = [float(entry.get()) for entry in self.alpha_entries]
        betas = [float(entry.get()) for entry in self.beta_entries]

        model_vars = pd.DataFrame()

        if self.selection_mode.get() == "column":
            for i, var in enumerate(selected_vars):
                numeric_data = pd.to_numeric(self.data[var], errors='coerce').dropna()
                model_vars[f"X_{i+1}"] = alphas[i] * betas[i] * numeric_data
        else:
            for i, var in enumerate(selected_vars):
                numeric_data = pd.to_numeric(self.data.loc[var], errors='coerce').dropna()
                model_vars[f"X_{i+1}"] = alphas[i] * betas[i] * numeric_data

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, model_vars)

def open_model_variables_window(parent, data):
    ModelVariablesWindow(parent, data)