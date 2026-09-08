import sqlite3
import tkinter as tk
from tkinter import messagebox


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("student_budget.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Budget (
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        monthly_budget REAL NOT NULL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL,
        date TEXT NOT NULL
    )
    """
)
conn.commit()


# =========================================================
# SET MONTHLY BUDGET
# =========================================================

def set_monthly_budget():
    budget = budget_entry.get().strip()

    if not budget:
        messagebox.showwarning("Input Error", "Please enter your monthly budget.")
        return

    try:
        budget = float(budget)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return

    if budget <= 0:
        messagebox.showwarning("Invalid Budget", "Budget must be greater than RM 0.")
        return

    user_id = 1
    cursor.execute("SELECT budget_id FROM Budget WHERE user_id = ?", (user_id,))

    if cursor.fetchone():
        cursor.execute(
            "UPDATE Budget SET monthly_budget = ? WHERE user_id = ?",
            (budget, user_id),
        )
    else:
        cursor.execute(
            "INSERT INTO Budget (user_id, monthly_budget) VALUES (?, ?)",
            (user_id, budget),
        )

    conn.commit()
    messagebox.showinfo("Budget Saved", f"Your monthly budget is RM {budget:.2f}")
    budget_entry.delete(0, tk.END)


# =========================================================
# ADD INCOME
# =========================================================

def add_income():
    amount = income_amount_entry.get().strip()
    category = income_category_entry.get().strip()
    date = income_date_entry.get().strip()

    if not amount or not category or not date:
        messagebox.showwarning("Input Error", "Please fill in all income details.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Amount", "Please enter a valid number.")
        return

    if amount <= 0:
        messagebox.showwarning("Invalid Amount", "Income must be greater than RM 0.")
        return

    cursor.execute(
        """
        INSERT INTO Transactions (user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (1, amount, category, "Income", date),
    )
    conn.commit()

    messagebox.showinfo("Income Added", f"Income of RM {amount:.2f} has been added.")
    income_amount_entry.delete(0, tk.END)
    income_category_entry.delete(0, tk.END)
    income_date_entry.delete(0, tk.END)


# =========================================================
# CURRENT BALANCE
# =========================================================

def calculate_balance():
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = ? AND type = 'Income'
        """,
        (1,),
    )
    total_income = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = ? AND type = 'Expense'
        """,
        (1,),
    )
    total_expenses = cursor.fetchone()[0]

    balance = total_income - total_expenses
    messagebox.showinfo(
        "Current Balance",
        f"Total Income: RM {total_income:.2f}\n"
        f"Total Expenses: RM {total_expenses:.2f}\n"
        f"Current Balance: RM {balance:.2f}",
    )


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense():
    amount = expense_amount_entry.get().strip()
    category = expense_category_var.get()
    date = expense_date_entry.get().strip()

    if not amount or not category or not date:
        messagebox.showwarning("Input Error", "Please fill in all expense details.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Amount", "Please enter a valid number.")
        return

    if amount <= 0:
        messagebox.showwarning("Invalid Amount", "Expense must be greater than RM 0.")
        return

    cursor.execute(
        """
        INSERT INTO Transactions (user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (1, amount, category, "Expense", date),
    )
    conn.commit()

    messagebox.showinfo("Expense Added", f"Expense of RM {amount:.2f} has been added.")
    expense_amount_entry.delete(0, tk.END)
    expense_category_var.set("Food")
    expense_date_entry.delete(0, tk.END)


# =========================================================
# GUI
# =========================================================

root = tk.Tk()
root.title("Student Budget Tracker")
root.geometry("500x700")


# ---------------- MONTHLY BUDGET ----------------

tk.Label(root, text="Set Monthly Budget", font=("Arial", 20, "bold")).pack(pady=5)
tk.Label(root, text="Monthly Budget (RM):", font=("Arial", 11)).pack()

budget_entry = tk.Entry(root, width=25, font=("Arial", 11))
budget_entry.pack(pady=2)

tk.Button(
    root,
    text="Save Budget",
    font=("Arial", 11, "bold"),
    command=set_monthly_budget,
).pack(pady=4)


# ---------------- ADD INCOME ----------------

tk.Label(root, text="Add Income", font=("Arial", 18, "bold")).pack(pady=4)
tk.Label(root, text="Income Amount (RM):").pack()

income_amount_entry = tk.Entry(root, width=25)
income_amount_entry.pack(pady=2)

tk.Label(root, text="Income Category:").pack()
income_category_entry = tk.Entry(root, width=25)
income_category_entry.pack(pady=2)

tk.Label(root, text="Date (YYYY-MM-DD):").pack()
income_date_entry = tk.Entry(root, width=25)
income_date_entry.pack(pady=2)

tk.Button(
    root,
    text="Add Income",
    font=("Arial", 11, "bold"),
    command=add_income,
).pack(pady=15)


# ---------------- ADD EXPENSE ----------------

tk.Label(root, text="Add Expense", font=("Arial", 18, "bold")).pack(pady=15)
tk.Label(root, text="Expense Amount (RM):").pack()

expense_amount_entry = tk.Entry(root, width=25)
expense_amount_entry.pack(pady=2)

tk.Label(root, text="Expense Category:").pack()
expense_category_var = tk.StringVar(value="Food")

tk.OptionMenu(
    root,
    expense_category_var,
    "Food",
    "Transport",
    "Shopping",
    "Bills",
).pack(pady=2)

tk.Label(root, text="Date (YYYY-MM-DD):").pack()
expense_date_entry = tk.Entry(root, width=25)
expense_date_entry.pack(pady=2)

tk.Button(
    root,
    text="Add Expense",
    font=("Arial", 11, "bold"),
    command=add_expense,
).pack(pady=2)

tk.Button(
    root,
    text="Calculate Current Balance",
    command=calculate_balance,
).pack(pady=2)


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()
conn.close()
