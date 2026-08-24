import tkinter as tk
from tkinter import messagebox
import sqlite3


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("student_budget.db")
cursor = conn.cursor()

# Budget table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Budget (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    monthly_budget REAL NOT NULL
)
""")

# Transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

conn.commit()


# =========================================================
# TASK 1 - SET MONTHLY BUDGET
# =========================================================

def set_monthly_budget():
    budget = budget_entry.get().strip()

    # Check empty input
    if budget == "":
        messagebox.showwarning(
            "Input Error",
            "Please enter your monthly budget."
        )
        return

    # Convert to number
    try:
        budget = float(budget)
    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid number."
        )
        return

    # Check positive number
    if budget <= 0:
        messagebox.showwarning(
            "Invalid Budget",
            "Budget must be greater than RM 0."
        )
        return

    # Temporary user ID
    user_id = 1

    # Check whether budget already exists
    cursor.execute(
        "SELECT budget_id FROM Budget WHERE user_id = ?",
        (user_id,)
    )

    existing_budget = cursor.fetchone()

    if existing_budget:
        # Update existing budget
        cursor.execute("""
            UPDATE Budget
            SET monthly_budget = ?
            WHERE user_id = ?
        """, (budget, user_id))
    else:
        # Insert new budget
        cursor.execute("""
            INSERT INTO Budget (user_id, monthly_budget)
            VALUES (?, ?)
        """, (user_id, budget))

    conn.commit()

    messagebox.showinfo(
        "Budget Saved",
        f"Your monthly budget is RM {budget:.2f}"
    )

    budget_entry.delete(0, tk.END)


# =========================================================
# TASK 2 - ADD INCOME
# =========================================================

def add_income():
    amount = income_amount_entry.get().strip()
    category = income_category_entry.get().strip()
    date = income_date_entry.get().strip()

    # Check empty fields
    if amount == "" or category == "" or date == "":
        messagebox.showwarning(
            "Input Error",
            "Please fill in all income details."
        )
        return

    # Convert amount to number
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid amount."
        )
        return

    # Check positive amount
    if amount <= 0:
        messagebox.showwarning(
            "Invalid Amount",
            "Income amount must be greater than RM 0."
        )
        return

    # Temporary user ID
    user_id = 1

    # Save income into Transactions table
    cursor.execute("""
        INSERT INTO Transactions
        (user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        amount,
        category,
        "Income",
        date
    ))

    conn.commit()

    messagebox.showinfo(
        "Income Added",
        f"Income of RM {amount:.2f} has been added."
    )

    # Clear the input boxes
    income_amount_entry.delete(0, tk.END)
    income_category_entry.delete(0, tk.END)
    income_date_entry.delete(0, tk.END)


# =========================================================
# GUI
# =========================================================

root = tk.Tk()
root.title("Student Budget Tracker")
root.geometry("500x650")


# =========================================================
# MONTHLY BUDGET SECTION
# =========================================================

title_label = tk.Label(
    root,
    text="Set Monthly Budget",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=20)


budget_label = tk.Label(
    root,
    text="Monthly Budget (RM):",
    font=("Arial", 12)
)
budget_label.pack()


budget_entry = tk.Entry(
    root,
    width=25,
    font=("Arial", 12)
)
budget_entry.pack(pady=5)


save_button = tk.Button(
    root,
    text="Save Budget",
    font=("Arial", 11, "bold"),
    command=set_monthly_budget
)
save_button.pack(pady=15)


# =========================================================
# ADD INCOME SECTION
# =========================================================

income_title = tk.Label(
    root,
    text="Add Income",
    font=("Arial", 18, "bold")
)
income_title.pack(pady=15)


# Income amount
income_amount_label = tk.Label(
    root,
    text="Income Amount (RM):",
    font=("Arial", 11)
)
income_amount_label.pack()


income_amount_entry = tk.Entry(
    root,
    width=25,
    font=("Arial", 11)
)
income_amount_entry.pack(pady=5)


# Income category
income_category_label = tk.Label(
    root,
    text="Income Category:",
    font=("Arial", 11)
)
income_category_label.pack()


income_category_entry = tk.Entry(
    root,
    width=25,
    font=("Arial", 11)
)
income_category_entry.pack(pady=5)


# Income date
income_date_label = tk.Label(
    root,
    text="Date (YYYY-MM-DD):",
    font=("Arial", 11)
)
income_date_label.pack()


income_date_entry = tk.Entry(
    root,
    width=25,
    font=("Arial", 11)
)
income_date_entry.pack(pady=5)


# Add Income buttondir

add_income_button = tk.Button(
    root,
    text="Add Income",
    font=("Arial", 11, "bold"),
    command=add_income
)
add_income_button.pack(pady=15)


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()


# Close database connection
conn.close()
