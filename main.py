import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

DATA_FILE = 'expenses.json'

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        self.expenses = []

        self.load_data()

        # Ввод данных
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_amount = tk.Entry(root)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.combo_category = ttk.Combobox(root, textvariable=self.category_var)
        self.combo_category['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Другое')
        self.combo_category.current(0)
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_date = tk.Entry(root)
        self.entry_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_date.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка добавить
        btn_add = tk.Button(root, text="Добавить расход", command=self.add_expense)
        btn_add.grid(row=0, column=6, padx=5, pady=5)

        # Таблица расходов
        self.tree = ttk.Treeview(root, columns=("amount", "category", "date"), show='headings')
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.grid(row=1, column=0, columnspan=7, padx=5, pady=5)

        # Заполняем таблицу
        self.refresh_table()

        # Фильтр по дате и категории
        tk.Label(root, text="Фильтр по категории:").grid(row=2, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.combo_filter_category = ttk.Combobox(root, textvariable=self.filter_category_var)
        self.combo_filter_category['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 'Другое')
        self.combo_filter_category.current(0)
        self.combo_filter_category.grid(row=2, column=1, padx=5, pady=5)
        self.combo_filter_category.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        tk.Label(root, text="Фильтр по дате (начало):").grid(row=2, column=2, padx=5, pady=5)
        self.entry_filter_date_start = tk.Entry(root)
        self.entry_filter_date_start.grid(row=2, column=3, padx=5, pady=5)

        tk.Label(root, text="по дате (конец):").grid(row=2, column=4, padx=5, pady=5)
        self.entry_filter_date_end = tk.Entry(root)
        self.entry_filter_date_end.grid(row=2, column=5, padx=5, pady=5)

        btn_filter = tk.Button(root, text="Применить фильтр", command=self.apply_filters)
        btn_filter.grid(row=2, column=6, padx=5, pady=5)

        # Итоговая сумма за выбранный период
        self.label_total = tk.Label(root, text="Общая сумма: 0")
        self.label_total.grid(row=3, column=0, columnspan=7, padx=5, pady=5)

        # Обновление суммы
        self.update_total()

    def load_data(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def refresh_table(self, filtered_expenses=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        data_source = filtered_expenses if filtered_expenses is not None else self.expenses
        for exp in data_source:
            self.tree.insert('', 'end', values=(exp['amount'], exp['category'], exp['date']))

    def add_expense(self):
        amount_str = self.entry_amount.get()
        category = self.category_var.get()
        date_str = self.entry_date.get()

        # Валидация
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число для суммы.")
            return

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ГГГГ-ММ-ДД.")
            return

        new_expense = {'amount': amount, 'category': category, 'date': date_str}
        self.expenses.append(new_expense)
        self.save_data()
        self.refresh_table()
        self.update_total()

        # Очистка полей
        self.entry_amount.delete(0, tk.END)

    def apply_filters(self):
        category_filter = self.filter_category_var.get()
        date_start = self.entry_filter_date_start.get()
        date_end = self.entry_filter_date_end.get()

        filtered = self.expenses

        if category_filter != 'Все':
            filtered = [e for e in filtered if e['category'] == category_filter]

        # Фильтр по дате
        try:
            if date_start:
                dt_start = datetime.strptime(date_start, '%Y-%m-%d')
                filtered = [e for e in filtered if datetime.strptime(e['date'], '%Y-%m-%d') >= dt_start]
            if date_end:
                dt_end = datetime.strptime(date_end, '%Y-%m-%d')
                filtered = [e for e in filtered if datetime.strptime(e['date'], '%Y-%m-%d') <= dt_end]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты для фильтра.")
            return

        self.refresh_table(filtered)
        self.update_total(filtered)

    def update_total(self, expenses_list=None):
        expenses_list = expenses_list if expenses_list is not None else self.expenses
        total = sum(e['amount'] for e in expenses_list)
        self.label_total.config(text=f"Общая сумма: {total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
