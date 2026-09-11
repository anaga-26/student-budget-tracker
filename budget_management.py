import sqlite3
import matplotlib.pyplot as plt
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

def calculate_remaining_budget():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT monthly_budget
        FROM Budget
        WHERE user_id = 1
    """)
    budget_result = cursor.fetchone()

    if budget_result is None:
        messagebox.showerror("Error", "Please set your monthly budget first.")
        return

    monthly_budget = budget_result[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
    """)
    total_expenses = cursor.fetchone()[0]

    remaining_budget = monthly_budget - total_expenses

    messagebox.showinfo(
        "Remaining Budget",
        f"Monthly Budget: RM {monthly_budget:.2f}\n"
        f"Total Expenses: RM {total_expenses:.2f}\n"
        f"Remaining Budget: RM {remaining_budget:.2f}"
    )
def display_total_income():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Income'
    """)

    total_income = cursor.fetchone()[0]

    messagebox.showinfo(
        "Total Income",
        f"Total Income: RM {total_income:.2f}"
    )

def display_total_expenses():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
    """)

    total_expenses = cursor.fetchone()[0]

    messagebox.showinfo(
        "Total Expenses",
        f"Total Expenses: RM {total_expenses:.2f}"
    )

def view_transaction_history():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type, amount, category, date
        FROM Transactions
        WHERE user_id = 1
        ORDER BY date DESC
    """)
    transactions = cursor.fetchall()

    history_window = tk.Toplevel(root)
    history_window.title("Transaction History")
    history_window.geometry("500x400")

    text_box = tk.Text(history_window, font=("Arial", 11))
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    if not transactions:
        text_box.insert(tk.END, "No transactions found.")
    else:
        for transaction_type, amount, category, date in transactions:
            text_box.insert(
                tk.END,
                f"{date} | {transaction_type} | {category} | RM {amount:.2f}\n"
            )

    text_box.config(state="disabled")

def calculate_remaining_balance():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Income'
    """)
    total_income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
    """)
    total_expenses = cursor.fetchone()[0]

    remaining_balance = total_income - total_expenses

    messagebox.showinfo(
        "Remaining Balance",
        f"Total Income: RM {total_income:.2f}\n"
        f"Total Expenses: RM {total_expenses:.2f}\n"
        f"Remaining Balance: RM {remaining_balance:.2f}"
    )

def display_budget_warning():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT monthly_budget
        FROM Budget
        WHERE user_id = 1
    """)
    budget_result = cursor.fetchone()

    if budget_result is None:
        messagebox.showerror(
            "No Budget Set",
            "Please set your monthly budget first."
        )
        return

    monthly_budget = budget_result[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
    """)
    total_expenses = cursor.fetchone()[0]

    if total_expenses > monthly_budget:
        exceeded_amount = total_expenses - monthly_budget
        messagebox.showwarning(
            "Budget Warning",
            f"You exceeded your budget by RM {exceeded_amount:.2f}!"
        )
    else:
        messagebox.showinfo(
            "Budget Status",
            f"You are within your budget.\n"
            f"Remaining budget: RM {monthly_budget - total_expenses:.2f}"
        )

def track_spending_by_category():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)
    category_totals = cursor.fetchall()

    category_window = tk.Toplevel(root)
    category_window.title("Spending by Category")
    category_window.geometry("400x300")

    text_box = tk.Text(category_window, font=("Arial", 12))
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    if not category_totals:
        text_box.insert(tk.END, "No expense records found.")
    else:
        for category, total in category_totals:
            text_box.insert(tk.END, f"{category}: RM {total:.2f}\n")

    text_box.config(state="disabled")

def generate_spending_charts():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)
    category_totals = cursor.fetchall()

    if not category_totals:
        messagebox.showinfo(
            "No Data",
            "Please add at least one expense before generating charts."
        )
        return

    categories = [item[0] for item in category_totals]
    totals = [item[1] for item in category_totals]

    figure, charts = plt.subplots(1, 2, figsize=(10, 4))

    charts[0].pie(totals, labels=categories, autopct="%1.1f%%")
    charts[0].set_title("Spending by Category")

    charts[1].bar(categories, totals, color="skyblue")
    charts[1].set_title("Expense Amounts")
    charts[1].set_xlabel("Category")
    charts[1].set_ylabel("Amount (RM)")

    figure.tight_layout()
    plt.show()

def generate_financial_report():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Income'
    """)
    total_income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = 1 AND type = 'Expense'
    """)
    total_expenses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT monthly_budget
        FROM Budget
        WHERE user_id = 1
    """)
    budget_result = cursor.fetchone()

    monthly_budget = budget_result[0] if budget_result else 0
    remaining_balance = total_income - total_expenses
    remaining_budget = monthly_budget - total_expenses

    messagebox.showinfo(
        "Financial Report",
        f"Monthly Budget: RM {monthly_budget:.2f}\n"
        f"Total Income: RM {total_income:.2f}\n"
        f"Total Expenses: RM {total_expenses:.2f}\n"
        f"Remaining Balance: RM {remaining_balance:.2f}\n"
        f"Remaining Budget: RM {remaining_budget:.2f}"
    )

def edit_transaction():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, type, amount, category, date
        FROM Transactions
        WHERE user_id = 1
        ORDER BY date DESC
    """)
    transactions = cursor.fetchall()

    if not transactions:
        messagebox.showinfo("No Transactions", "There are no transactions to edit.")
        return

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Transaction")
    edit_window.geometry("500x500")

    tk.Label(
        edit_window,
        text="Current Transactions",
        font=("Arial", 14, "bold")
    ).pack(pady=8)

    transaction_text = tk.Text(edit_window, height=10, font=("Arial", 10))
    transaction_text.pack(fill="x", padx=10)

    for transaction_id, transaction_type, amount, category, date in transactions:
        transaction_text.insert(
            tk.END,
            f"ID {transaction_id} | {date} | {transaction_type} | "
            f"{category} | RM {amount:.2f}\n"
        )

    transaction_text.config(state="disabled")

    tk.Label(edit_window, text="Transaction ID to edit:").pack(pady=(10, 0))
    transaction_id_entry = tk.Entry(edit_window, width=25)
    transaction_id_entry.pack()

    tk.Label(edit_window, text="New amount (RM):").pack(pady=(8, 0))
    amount_entry = tk.Entry(edit_window, width=25)
    amount_entry.pack()

    tk.Label(edit_window, text="New category:").pack(pady=(8, 0))
    category_entry = tk.Entry(edit_window, width=25)
    category_entry.pack()

    tk.Label(edit_window, text="New date (YYYY-MM-DD):").pack(pady=(8, 0))
    date_entry = tk.Entry(edit_window, width=25)
    date_entry.pack()

    def save_transaction_changes():
        transaction_id = transaction_id_entry.get().strip()
        amount = amount_entry.get().strip()
        category = category_entry.get().strip()
        date = date_entry.get().strip()

        if not transaction_id or not amount or not category or not date:
            messagebox.showwarning("Input Error", "Please fill in every field.")
            return

        try:
            transaction_id = int(transaction_id)
            amount = float(amount)
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Transaction ID must be a whole number and amount must be a number."
            )
            return

        cursor.execute("""
            UPDATE Transactions
            SET amount = ?, category = ?, date = ?
            WHERE transaction_id = ? AND user_id = 1
        """, (amount, category, date, transaction_id))

        if cursor.rowcount == 0:
            messagebox.showerror("Not Found", "Transaction ID was not found.")
            return

        conn.commit()
        messagebox.showinfo("Success", "Transaction updated successfully.")
        edit_window.destroy()

    tk.Button(
        edit_window,
        text="Save Changes",
        font=("Arial", 11, "bold"),
        command=save_transaction_changes,
    ).pack(pady=15)

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

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root = scrollable_frame

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

tk.Button(
    root,
    text="Check Remaining Budget",
    font=("Arial", 11, "bold"),
    command=calculate_remaining_budget,
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


tk.Button(
    root,
    text="Display Total Income",
    font=("Arial", 11, "bold"),
    command=display_total_income,
).pack(pady=4)
tk.Button(
    root,
    text="Display Total Expenses",
    font=("Arial", 11, "bold"),
    command=display_total_expenses,
).pack(pady=4)
tk.Button(
    root,
    text="View Transaction History",
    font=("Arial", 11, "bold"),
    command=view_transaction_history,
).pack(pady=4)
tk.Button(
    root,
    text="Check Remaining Balance",
    font=("Arial", 11, "bold"),
    command=calculate_remaining_balance,
).pack(pady=4)
tk.Button(
    root,
    text="Display Budget Warning",
    font=("Arial", 11, "bold"),
    command=display_budget_warning,
).pack(pady=4)
tk.Button(
    root,
    text="Track Spending by Category",
    font=("Arial", 11, "bold"),
    command=track_spending_by_category,
).pack(pady=4)

tk.Button(
    root,
    text="Generate Spending Charts",
    font=("Arial", 11, "bold"),
    command=generate_spending_charts,
).pack(pady=4)
tk.Button(
    root,
    text="Generate Financial Report",
    font=("Arial", 11, "bold"),
    command=generate_financial_report,
).pack(pady=4)
tk.Button(
    root,
    text="Edit Transaction",
    font=("Arial", 11, "bold"),
    command=edit_transaction,
).pack(pady=4)
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
