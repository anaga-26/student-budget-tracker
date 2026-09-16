import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# -----------------------------
# Database
# -----------------------------

DB_NAME = "budget_tracker.db"

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Daily Necessities",
    "Other"
]

INCOME_SOURCES = [
    "Monthly Allowance",
    "Part-Time Job",
    "Scholarship",
    "Other"
]


class StudentBudgetTracker:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Budget Tracker")
        self.root.geometry("700x500")

        # Connect to SQLite
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()

        self.create_database()

        self.build_interface()

    # -----------------------------
    # Create Database
    # -----------------------------

    def create_database(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                description TEXT,
                income_source TEXT,
                notes TEXT
            )
        """)

        self.conn.commit()

    # -----------------------------
    # Main Interface
    # -----------------------------

    def build_interface(self):

        title = tk.Label(
            self.root,
            text="Student Budget Tracker",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=20)

        subtitle = tk.Label(
            self.root,
            text="Income and Expense Recording",
            font=("Arial", 12)
        )
        subtitle.pack(pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=30)

        income_button = tk.Button(
            button_frame,
            text="Add Income",
            width=20,
            height=2,
            command=lambda: self.open_transaction_form("Income")
        )
        income_button.grid(row=0, column=0, padx=10)

        expense_button = tk.Button(
            button_frame,
            text="Add Expense",
            width=20,
            height=2,
            command=lambda: self.open_transaction_form("Expense")
        )
        expense_button.grid(row=0, column=1, padx=10)

        view_button = tk.Button(
            self.root,
            text="View Recorded Transactions",
            width=30,
            height=2,
            command=self.view_transactions
        )
        view_button.pack(pady=20)

    # -----------------------------
    # Transaction Form
    # -----------------------------

    def open_transaction_form(self, transaction_type):

        window = tk.Toplevel(self.root)

        if transaction_type == "Income":
            window.title("Add Income")
        else:
            window.title("Add Expense")

        window.geometry("450x400")
        window.resizable(False, False)

        form = ttk.Frame(window, padding=20)
        form.pack(fill="both", expand=True)

        # Amount
        ttk.Label(
            form,
            text="Amount (RM)"
        ).grid(row=0, column=0, sticky="w", pady=8)

        amount_entry = ttk.Entry(form, width=30)
        amount_entry.grid(row=0, column=1, pady=8)

        # Date
        ttk.Label(
            form,
            text="Date (YYYY-MM-DD)"
        ).grid(row=1, column=0, sticky="w", pady=8)

        date_entry = ttk.Entry(form, width=30)
        date_entry.insert(
            0,
            datetime.today().strftime("%Y-%m-%d")
        )
        date_entry.grid(row=1, column=1, pady=8)

        # Category / Income Source
        if transaction_type == "Income":

            ttk.Label(
                form,
                text="Income Source"
            ).grid(row=2, column=0, sticky="w", pady=8)

            source_combo = ttk.Combobox(
                form,
                values=INCOME_SOURCES,
                state="readonly",
                width=27
            )
            source_combo.current(0)
            source_combo.grid(row=2, column=1, pady=8)

        else:

            ttk.Label(
                form,
                text="Expense Category"
            ).grid(row=2, column=0, sticky="w", pady=8)

            category_combo = ttk.Combobox(
                form,
                values=EXPENSE_CATEGORIES,
                state="readonly",
                width=27
            )
            category_combo.current(0)
            category_combo.grid(row=2, column=1, pady=8)

        # Description
        ttk.Label(
            form,
            text="Description"
        ).grid(row=3, column=0, sticky="w", pady=8)

        description_entry = ttk.Entry(form, width=30)
        description_entry.grid(row=3, column=1, pady=8)

        # Notes
        ttk.Label(
            form,
            text="Notes"
        ).grid(row=4, column=0, sticky="w", pady=8)

        notes_entry = ttk.Entry(form, width=30)
        notes_entry.grid(row=4, column=1, pady=8)

        # -----------------------------
        # Save Transaction
        # -----------------------------

        def save_transaction():

            # Validate amount
            try:
                amount = float(
                    amount_entry.get().strip()
                )

                if amount <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid Amount",
                    "Please enter an amount greater than 0."
                )
                return

            # Validate date
            transaction_date = date_entry.get().strip()

            try:
                datetime.strptime(
                    transaction_date,
                    "%Y-%m-%d"
                )

            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    "Please enter a valid date in YYYY-MM-DD format."
                )
                return

            # Get description
            description = description_entry.get().strip()

            if description == "":
                description = "No description"

            # Get notes
            notes = notes_entry.get().strip()

            # Income
            if transaction_type == "Income":

                income_source = source_combo.get()

                category = "Income"

            # Expense
            else:

                income_source = ""

                category = category_combo.get()

            # Insert into SQLite
            self.cur.execute(
                """
                INSERT INTO transactions
                (
                    transaction_type,
                    amount,
                    date,
                    category,
                    description,
                    income_source,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction_type,
                    amount,
                    transaction_date,
                    category,
                    description,
                    income_source,
                    notes
                )
            )

            self.conn.commit()

            messagebox.showinfo(
                "Success",
                f"{transaction_type} recorded successfully!"
            )

            window.destroy()

        save_button = ttk.Button(
            form,
            text="Save Transaction",
            command=save_transaction
        )
        save_button.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=25
        )

    # -----------------------------
    # View Transactions
    # -----------------------------

    def view_transactions(self):

        window = tk.Toplevel(self.root)
        window.title("Recorded Transactions")
        window.geometry("750x400")

        columns = (
            "ID",
            "Type",
            "Amount",
            "Date",
            "Category",
            "Description"
        )

        tree = ttk.Treeview(
            window,
            columns=columns,
            show="headings"
        )

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=110)

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.cur.execute("""
            SELECT
                transaction_id,
                transaction_type,
                amount,
                date,
                category,
                description
            FROM transactions
            ORDER BY transaction_id DESC
        """)

        transactions = self.cur.fetchall()

        for transaction in transactions:
            tree.insert(
                "",
                "end",
                values=transaction
            )


# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = StudentBudgetTracker(root)

    root.mainloop()