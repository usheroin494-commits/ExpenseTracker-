import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkinter import filedialog

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Личный трекер расходов")
        self.root.geometry("800x600")

        # Данные: список расходов
        self.expenses = []
        self.data_file = "expenses.json"

        # Загрузка данных при старте
        self.load_data()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

    def create_widgets(self):
        # === Рамка ввода данных ===
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=18)
        self.category_combo['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Коммунальные услуги', 'Здоровье', 'Другое')
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="➕ Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # === Рамка фильтрации ===
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=18)
        self.filter_combo['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 'Коммунальные услуги', 'Здоровье', 'Другое')
        self.filter_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Дата с (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="по:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        self.filter_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=6, padx=10, pady=5)

        self.reset_filter_btn = ttk.Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=7, padx=5, pady=5)

        # === Рамка с итоговой суммой ===
        sum_frame = ttk.Frame(self.root)
        sum_frame.pack(fill="x", padx=10, pady=5)
        self.total_label = ttk.Label(sum_frame, text="Сумма за период: 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=10)

        # === Таблица расходов ===
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (руб)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")

        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=120)
        self.tree.column("Категория", width=150)
        self.tree.column("Дата", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления выбранной записи
        self.delete_btn = ttk.Button(self.root, text="🗑 Удалить выбранный расход", command=self.delete_expense)
        self.delete_btn.pack(pady=5)

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        """Добавление нового расхода с проверкой"""
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_entry.get().strip()

        # Проверка суммы
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            return

        # Проверка категории
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return

        # Проверка даты
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        # Добавление
        new_id = len(self.expenses) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        })

        self.save_data()
        self.refresh_table()
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Расход добавлен!")

    def delete_expense(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        item = self.tree.item(selected[0])
        exp_id = item['values'][0]

        # Удаление по id
        self.expenses = [e for e in self.expenses if e["id"] != exp_id]

        # Перенумерация id
        for idx, exp in enumerate(self.expenses, start=1):
            exp["id"] = idx

        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись удалена!")

    def apply_filter(self):
        """Применение фильтра по категории и дате"""
        cat_filter = self.filter_category_var.get()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        filtered = self.expenses.copy()

        # Фильтр по категории
        if cat_filter != "Все":
            filtered = [e for e in filtered if e["category"] == cat_filter]

        # Фильтр по дате
        if start_date:
            if not self.validate_date(start_date):
                messagebox.showerror("Ошибка", "Неверный формат начальной даты!")
                return
            filtered = [e for e in filtered if e["date"] >= start_date]

        if end_date:
            if not self.validate_date(end_date):
                messagebox.showerror("Ошибка", "Неверный формат конечной даты!")
                return
            filtered = [e for e in filtered if e["date"] <= end_date]

        self.display_table(filtered)
        self.calculate_total(filtered)

    def reset_filter(self):
        """Сброс фильтра"""
        self.filter_category_var.set("Все")
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        """Обновление таблицы без фильтра"""
        self.display_table(self.expenses)
        self.calculate_total(self.expenses)

    def display_table(self, expenses_list):
        """Отображение списка расходов в таблице"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for exp in expenses_list:
            self.tree.insert("", "end", values=(
                exp["id"],
                f"{exp['amount']:.2f}",
                exp["category"],
                exp["date"]
            ))

    def calculate_total(self, expenses_list):
        """Подсчёт суммы за период (текущий фильтр)"""
        total = sum(exp["amount"] for exp in expenses_list)
        self.total_label.config(text=f"Сумма за период: {total:.2f} руб")

    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.expenses = []
        else:
            self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
    