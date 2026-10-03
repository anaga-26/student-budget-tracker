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

    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Student Budget Tracker")
        self.root.geometry("700x500")

        # Store last deleted transaction for Undo
        self.last_deleted_transaction = None

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
    user_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    category TEXT,
    description TEXT,
    income_source TEXT,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
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

    def open_transaction_form(
        self,
        transaction_type,
        transaction=None
    ):

        window = tk.Toplevel(self.root)

        if transaction is None:
            if transaction_type == "Income":
                window.title("Add Income")
            else:
                window.title("Add Expense")
        else:
            window.title("Edit Transaction")

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

        if transaction is None:
            date_entry.insert(
                0,
                datetime.today().strftime("%Y-%m-%d")
            )
        else:
            date_entry.insert(0, transaction[3])

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

            if transaction is not None:
                if transaction[6] in INCOME_SOURCES:
                    source_combo.set(transaction[6])

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

            if transaction is not None:
                if transaction[4] in EXPENSE_CATEGORIES:
                    category_combo.set(transaction[4])

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

        # Fill existing transaction data
        if transaction is not None:

            amount_entry.insert(0, str(transaction[2]))
            description_entry.insert(0, transaction[5])
            notes_entry.insert(0, transaction[7])

        # -----------------------------
        # Save / Update Transaction
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

            # Description
            description = description_entry.get().strip()

            if description == "":
                description = "No description"

            # Notes
            notes = notes_entry.get().strip()

            # Income
            if transaction_type == "Income":

                income_source = source_combo.get()
                category = "Income"

            # Expense
            else:

                income_source = ""
                category = category_combo.get()

            # -----------------------------
            # Update Existing Transaction
            # -----------------------------

            if transaction is not None:

                self.cur.execute(
                    """
                    UPDATE transactions

                    SET
                        transaction_type = ?,
                        amount = ?,
                        date = ?,
                        category = ?,
                        description = ?,
                        income_source = ?,
                        notes = ?

                    WHERE transaction_id = ? AND user_id = ?
                    """,
                    (
                        transaction_type,
                        amount,
                        transaction_date,
                        category,
                        description,
                        income_source,
                        notes,
                        transaction[0],
                        self.user_id
                    )
                )

                self.conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Transaction updated successfully!"
                )

            # -----------------------------
            # Add New Transaction
            # -----------------------------

            else:

                self.cur.execute(
                    """
                    INSERT INTO transactions
 (
             user_id,
             transaction_type,
             amount,
             date,
             category,
             description,
             income_source,
             notes
 )

         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
     (
    self.user_id,
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

        if transaction is None:

            button_text = "Save Transaction"

        else:

            button_text = "Update Transaction"

        save_button = ttk.Button(
            form,
            text=button_text,
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

        window.title("Transaction History")
        window.geometry("1050x600")

        # -----------------------------
        # Search and Filter Area
        # -----------------------------

        control_frame = ttk.Frame(
            window,
            padding=10
        )

        control_frame.pack(
            fill="x"
        )

        # Search
        ttk.Label(
            control_frame,
            text="Search:"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        search_entry = ttk.Entry(
            control_frame,
            width=25
        )

        search_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        # Type Filter
        ttk.Label(
            control_frame,
            text="Type:"
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        type_filter = ttk.Combobox(
            control_frame,
            values=[
                "All",
                "Income",
                "Expense"
            ],
            state="readonly",
            width=12
        )

        type_filter.set("All")

        type_filter.grid(
            row=0,
            column=3,
            padx=5
        )

        # Category Filter
        ttk.Label(
            control_frame,
            text="Category:"
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        category_filter = ttk.Combobox(
            control_frame,
            values=["All"] + EXPENSE_CATEGORIES,
            state="readonly",
            width=18
        )

        category_filter.set("All")

        category_filter.grid(
            row=0,
            column=5,
            padx=5
        )

        # Sort
        ttk.Label(
            control_frame,
            text="Sort:"
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=10
        )

        sort_combo = ttk.Combobox(
            control_frame,
            values=[
                "Newest First",
                "Oldest First",
                "Highest Amount",
                "Lowest Amount"
            ],
            state="readonly",
            width=18
        )

        sort_combo.set("Newest First")

        sort_combo.grid(
            row=1,
            column=1,
            padx=5,
            pady=10
        )

        # -----------------------------
        # Transaction Table
        # -----------------------------

        table_frame = ttk.Frame(window)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        columns = (
            "ID",
            "Type",
            "Amount",
            "Date",
            "Category",
            "Description",
            "Income Source",
            "Notes"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for column in columns:

            tree.heading(
                column,
                text=column
            )

        tree.column("ID", width=50)
        tree.column("Type", width=80)
        tree.column("Amount", width=80)
        tree.column("Date", width=100)
        tree.column("Category", width=120)
        tree.column("Description", width=150)
        tree.column("Income Source", width=130)
        tree.column("Notes", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # -----------------------------
        # Load Transactions
        # -----------------------------

        def load_transactions():

            # Clear table
            for item in tree.get_children():

                tree.delete(item)

            search_text = search_entry.get().strip().lower()

            selected_type = type_filter.get()
            selected_category = category_filter.get()
            selected_sort = sort_combo.get()

            # SQL sorting
            if selected_sort == "Newest First":

                order_by = "date DESC"

            elif selected_sort == "Oldest First":

                order_by = "date ASC"

            elif selected_sort == "Highest Amount":

                order_by = "amount DESC"

            else:

                order_by = "amount ASC"

            query = f"""
    SELECT
        transaction_id,
        transaction_type,
        amount,
        date,
        category,
        description,
        income_source,
        notes

    FROM transactions

    WHERE user_id = ?

    ORDER BY {order_by}
"""

            self.cur.execute(query, (self.user_id,))

            transactions = self.cur.fetchall()

            for transaction in transactions:

                transaction_id = transaction[0]
                transaction_type = transaction[1]
                category = transaction[4]
                description = transaction[5]
                income_source = transaction[6]
                notes = transaction[7]

                # Type filter
                if selected_type != "All":

                    if transaction_type != selected_type:
                        continue

                # Category filter
                if selected_category != "All":

                    if category != selected_category:
                        continue

                # Search
                searchable_text = (
                    str(transaction_id)
                    + " "
                    + str(transaction_type)
                    + " "
                    + str(category)
                    + " "
                    + str(description)
                    + " "
                    + str(income_source)
                    + " "
                    + str(notes)
                ).lower()

                if search_text not in searchable_text:
                    continue

                tree.insert(
                    "",
                    "end",
                    values=transaction
                )

        # -----------------------------
        # Edit Transaction
        # -----------------------------

        def edit_transaction():

            selected_item = tree.selection()

            if not selected_item:

                messagebox.showwarning(
                    "No Selection",
                    "Please select a transaction to edit."
                )

                return

            values = tree.item(
                selected_item[0],
                "values"
            )

            transaction_id = values[0]

            self.cur.execute(
                """
                SELECT
                    transaction_id,
                    transaction_type,
                    amount,
                    date,
                    category,
                    description,
                    income_source,
                    notes

                FROM transactions

                WHERE transaction_id = ? AND user_id = ?
                """,
                (transaction_id, self.user_id)
            )

            transaction = self.cur.fetchone()

            if transaction is None:

                messagebox.showerror(
                    "Error",
                    "Transaction could not be found."
                )

                return

            self.open_transaction_form(
                transaction[1],
                transaction
            )

            window.wait_window()

            load_transactions()

        # -----------------------------
        # Delete Transaction
        # -----------------------------

        def delete_transaction():

            selected_item = tree.selection()

            if not selected_item:

                messagebox.showwarning(
                    "No Selection",
                    "Please select a transaction to delete."
                )

                return

            values = tree.item(
                selected_item[0],
                "values"
            )

            transaction_id = values[0]

            # Get complete transaction
            self.cur.execute(
                """
                SELECT
                    transaction_id,
                    transaction_type,
                    amount,
                    date,
                    category,
                    description,
                    income_source,
                    notes

                FROM transactions

                WHERE transaction_id = ? AND user_id = ?
                """,
               (transaction_id, self.user_id)
            )

            transaction = self.cur.fetchone()

            if transaction is None:

                return

            # Confirmation
            confirmation = messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this transaction?"
            )

            if not confirmation:

                return

            # Save transaction for Undo
            self.last_deleted_transaction = transaction

            # Delete
            self.cur.execute(
                """
                DELETE FROM transactions
                WHERE transaction_id = ? AND user_id = ?
                """,
                (transaction_id, self.user_id)
            )

            self.conn.commit()

            messagebox.showinfo(
                "Deleted",
                "Transaction deleted successfully.\n"
                "You can use Undo to restore it."
            )

            load_transactions()

        # -----------------------------
        # Undo Delete
        # -----------------------------

        def undo_delete():

            if self.last_deleted_transaction is None:

                messagebox.showinfo(
                    "Undo",
                    "There is no deleted transaction to undo."
                )

                return

            transaction = self.last_deleted_transaction

            self.cur.execute(
                """
                INSERT INTO transactions
                (
    transaction_id,
    user_id,
    transaction_type,
    amount,
    date,
    category,
    description,
    income_source,
    notes
)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
               (
    transaction[0],
    self.user_id,
    transaction[1],
    transaction[2],
    transaction[3],
    transaction[4],
    transaction[5],
    transaction[6],
    transaction[7]
)
            )

            self.conn.commit()

            self.last_deleted_transaction = None

            messagebox.showinfo(
                "Undo",
                "Deleted transaction restored successfully!"
            )

            load_transactions()

        # -----------------------------
        # Buttons
        # -----------------------------

        button_frame = ttk.Frame(
            window,
            padding=10
        )

        button_frame.pack()

        ttk.Button(
            button_frame,
            text="Edit Transaction",
            command=edit_transaction
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Delete Transaction",
            command=delete_transaction
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Undo Delete",
            command=undo_delete
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Refresh",
            command=load_transactions
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Close",
            command=window.destroy
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        # Automatically update when controls change
        search_entry.bind(
            "<KeyRelease>",
            lambda event: load_transactions()
        )

        type_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: load_transactions()
        )

        category_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: load_transactions()
        )

        sort_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: load_transactions()
        )

        # Initial display
        load_transactions()

    # -----------------------------
    # Close Database
    # -----------------------------

    def close_database(self):

        self.conn.close()


# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = StudentBudgetTracker(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: (
            app.close_database(),
            root.destroy()
        )
    )

    root.mainloop()