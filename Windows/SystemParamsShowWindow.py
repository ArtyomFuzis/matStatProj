import tkinter as tk
from enum import EnumType
from tkinter import ttk

class AnswerType(EnumType):
    Continue = 0
    Return = 1

class SystemParamsShowWindow:
    def __init__(self, parent, params_for_rows: dict[any, tuple[int,int]], all_d: int , all_h: int):
        self.window = tk.Toplevel(parent)
        self.window.geometry("450x500")
        self.window.resizable(False, False)
        self.window.title("SystemParams")
        self.answer = AnswerType.Continue
        self.data_map = params_for_rows
        self.fail_flag = False

        self.lbl_general = ttk.Label(self.window, text=f"Всего эндогенных переменных: {all_h}, Экзогенных: {all_d}", font=("Arial", 10))
        self.lbl_general.pack(fill=tk.BOTH, pady=10, padx=15)

        # Создание контейнера для таблицы с прокруткой
        container = tk.Frame(self.window)
        container.pack(fill=tk.BOTH, expand=True, padx=10)

        # Создание таблицы
        self._create_table(container)
        self.btn_continue = ttk.Button(self.window, text="Продолжить",command=self.exit_continue)
        self.btn_continue.focus_set()
        if not self.fail_flag:
            self.btn_continue.pack(side=tk.LEFT, pady=10, padx=15)
        else:
            self.answer = AnswerType.Return

        self.btn_return = ttk.Button(self.window, text="Вернуться", command=self.exit_return)
        self.btn_return.pack(side=tk.LEFT, pady=10)

    def _create_table(self, parent):
        scrollbar_y = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            parent,
            columns=("row", "D", "H", "output"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        # Настраиваем прокрутку
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # Задаем заголовки колонок
        self.tree.heading("row", text="Номер")
        self.tree.heading("D", text="D")
        self.tree.heading("H", text="H")
        self.tree.heading("output", text="Вывод")

        # Настраиваем ширину колонок
        self.tree.column("row", width=50, anchor=tk.CENTER)
        self.tree.column("D", width=50, anchor=tk.CENTER)
        self.tree.column("H", width=50, anchor=tk.CENTER)
        self.tree.column("output", width=250, anchor=tk.CENTER)

        # Заполняем данными
        sorted_keys = sorted(self.data_map.keys())
        for key in sorted_keys:
            d_val, h_val = self.data_map[key]
            if d_val + 1 < h_val:
                out_res = "Неидентифицируемо"
                self.fail_flag = True
            elif d_val + 1 == h_val:
                out_res = "Идентифицируемо"
            else:
                out_res = "Сверхидентифицируемо"
            self.tree.insert("", tk.END, iid=key, values=(key, d_val, h_val, out_res))

        # Размещаем компоненты
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Настраиваем растягивание
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)


    def show(self) -> int:
        self.window.grab_set()
        self.window.wait_window()
        return self.answer

    def exit_continue(self):
        self.answer = AnswerType.Continue
        self.window.destroy()

    def exit_return(self):
        self.answer = AnswerType.Return
        self.window.destroy()

