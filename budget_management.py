import tkinter as tk
from tkinter import messagebox
import sqlite3


# ---------------- DATABASE ----------------

conn = sqlite3.connect("student_budget.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Budget (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    monthly_budget REAL NOT NULL
)
""")

conn.commit()


# ---------------- SET MONTHLY BUDGET ----------------

def set_monthly_budget():
    budget = budget_entry.get().strip()

    # Check if the input is empty
    if budget == "":
        messagebox.showwarning(
            "Input Error",
            "Please enter your monthly budget."
        )
        return

    # Convert the input to a number
    try:
        budget = float(budget)
    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid number."
        )
        return

    # Check if the budget is greater than 0
    if budget <= 0:
        messagebox.showwarning(
            "Invalid Budget",
            "Budget must be greater than RM 0."
        )
        return

    # Temporary user ID for testing
    user_id = 1

    # Check if the user already has a budget
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
        # Add a new budget
        cursor.execute("""
            INSERT INTO Budget (user_id, monthly_budget)
            VALUES (?, ?)
        """, (user_id, budget))

    # Save changes
    conn.commit()

    # Show success message
    messagebox.showinfo(
        "Budget Saved",
        f"Your monthly budget is RM {budget:.2f}"
    )

    # Clear the input box
    budget_entry.delete(0, tk.END)


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Student Budget Tracker")
root.geometry("450x300")


title_label = tk.Label(
    root,
    text="Set Monthly Budget",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=30)


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
budget_entry.pack(pady=10)


save_button = tk.Button(
    root,
    text="Save Budget",
    font=("Arial", 11, "bold"),
    command=set_monthly_budget
)
save_button.pack(pady=20)


# Start the application
root.mainloop()


# Close database connection
conn.close()
Student-Budget-Tracker/budget_management.py