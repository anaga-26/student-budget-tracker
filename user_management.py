import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import date
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# =========================================================
# APPLICATION SETTINGS
# =========================================================

USER_DB = "budget_tracker.db"
FINANCE_DB = "student_budget.db"

NAVY = "#10213F"
NAVY_2 = "#16345C"
TEAL = "#0F9D92"
TEAL_DARK = "#087A72"
TEAL_LIGHT = "#E6F7F4"
BG = "#F5F8FA"
WHITE = "#FFFFFF"
TEXT = "#18263D"
MUTED = "#68758A"
BORDER = "#DCE4EA"
GREEN = "#159B73"
RED = "#E35D6A"
YELLOW = "#E8A92E"
BLUE = "#3D8ED0"

root = tk.Tk()
root.title("Student Budget Tracker")
root.geometry("1180x760")
root.minsize(1050, 680)
root.configure(bg=BG)

logged_in_user_id = None
profile_photo = None
profile_photo_path = None
content_frame = None
page_title_label = None
page_subtitle_label = None
sidebar_buttons = {}

# Form variables
budget_var = tk.StringVar()
income_amount_var = tk.StringVar()
income_category_var = tk.StringVar(value="Allowance")
expense_amount_var = tk.StringVar()
expense_category_var = tk.StringVar(value="Food")
transaction_date_var = tk.StringVar(value=date.today().isoformat())
profile_username_var = tk.StringVar()
profile_password_var = tk.StringVar()
profile_confirm_var = tk.StringVar()


# =========================================================
# DATABASE HELPERS
# =========================================================

def create_databases():
    connection = sqlite3.connect(USER_DB)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

    connection = sqlite3.connect(FINANCE_DB)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Budget (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            monthly_budget REAL NOT NULL
        )
    """)
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
    connection.commit()
    connection.close()


def finance_connection():
    return sqlite3.connect(FINANCE_DB)


def get_financial_summary():
    if logged_in_user_id is None:
        return 0, 0, 0, 0

    connection = finance_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT monthly_budget FROM Budget WHERE user_id = ?",
        (logged_in_user_id,)
    )
    result = cursor.fetchone()
    budget = result[0] if result else 0

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = ? AND type = 'Income'
    """, (logged_in_user_id,))
    income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = ? AND type = 'Expense'
    """, (logged_in_user_id,))
    expenses = cursor.fetchone()[0]

    connection.close()
    return budget, income, expenses, income - expenses


def get_username():
    if logged_in_user_id is None:
        return "Student"

    connection = sqlite3.connect(USER_DB)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT username FROM users WHERE user_id = ?",
        (logged_in_user_id,)
    )
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else "Student"


# =========================================================
# SMALL UI HELPERS
# =========================================================

def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


def make_button(parent, text, command, width=None, primary=False):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 10, "bold"),
        fg=WHITE if primary else TEXT,
        bg=TEAL if primary else WHITE,
        activeforeground=WHITE if primary else TEXT,
        activebackground=TEAL_DARK if primary else TEAL_LIGHT,
        relief="flat" if primary else "solid",
        bd=0 if primary else 1,
        cursor="hand2",
        padx=14,
        pady=9
    )
    if width:
        button.config(width=width)
    return button


def card(parent, title, value, accent=TEAL):
    frame = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    top = tk.Frame(frame, bg=accent, height=4)
    top.pack(fill="x")
    tk.Label(
        frame, text=title, bg=WHITE, fg=MUTED,
        font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=16, pady=(14, 4))
    value_label = tk.Label(
        frame, text=value, bg=WHITE, fg=TEXT,
        font=("Arial", 17, "bold")
    )
    value_label.pack(anchor="w", padx=16, pady=(0, 14))
    return frame, value_label


def field(parent, label_text, variable, show=None):
    wrapper = tk.Frame(parent, bg=WHITE)
    tk.Label(
        wrapper, text=label_text, bg=WHITE, fg=TEXT,
        font=("Arial", 9, "bold")
    ).pack(anchor="w", pady=(0, 5))
    entry = tk.Entry(
        wrapper, textvariable=variable, show=show,
        font=("Arial", 10), relief="solid", bd=1,
        highlightthickness=1, highlightcolor=TEAL
    )
    entry.pack(fill="x", ipady=7)
    return wrapper, entry


def set_page_header(title, subtitle):
    page_title_label.config(text=title)
    page_subtitle_label.config(text=subtitle)


# =========================================================
# LOGIN / REGISTER
# =========================================================

def register_user():
    username = register_username.get().strip()
    password = register_password.get()
    confirm = register_confirm.get()

    if not username or not password or not confirm:
        messagebox.showwarning("Missing details", "Please complete all fields.")
        return

    if password != confirm:
        messagebox.showwarning("Password mismatch", "The passwords do not match.")
        return

    connection = sqlite3.connect(USER_DB)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password)
        )
        connection.commit()
        messagebox.showinfo("Account created", "Your account has been created.")
        show_login()
    except sqlite3.IntegrityError:
        messagebox.showerror("Username unavailable", "That username is already in use.")
    finally:
        connection.close()


def login_user():
    global logged_in_user_id

    username = login_username.get().strip()
    password = login_password.get()

    if not username or not password:
        messagebox.showwarning("Missing details", "Enter your username and password.")
        return

    connection = sqlite3.connect(USER_DB)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    result = cursor.fetchone()
    connection.close()

    if result:
        logged_in_user_id = result[0]
        show_app()
    else:
        messagebox.showerror("Login failed", "Incorrect username or password.")


def show_login():
    global login_username, login_password

    clear_root()
    root.geometry("900x600")
    root.resizable(False, False)

    outer = tk.Frame(root, bg=BG)
    outer.pack(fill="both", expand=True)

    left = tk.Frame(outer, bg=NAVY, width=370)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    tk.Label(
        left, text="Student\nBudget Tracker",
        bg=NAVY, fg=WHITE,
        font=("Arial", 27, "bold"),
        justify="left"
    ).pack(anchor="w", padx=42, pady=(70, 12))

    tk.Label(
        left, text="Manage your money.\nBuild better habits.",
        bg=NAVY, fg="#61D9D0",
        font=("Arial", 12),
        justify="left"
    ).pack(anchor="w", padx=42)

    # Simple hand-built visual instead of an external image.
    visual = tk.Frame(left, bg=NAVY)
    visual.pack(fill="both", expand=True, padx=42, pady=30)

    canvas = tk.Canvas(visual, bg=NAVY, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_oval(30, 80, 250, 300, fill=NAVY_2, outline="")
    canvas.create_rectangle(95, 235, 285, 330, fill="#244D75", outline="")
    canvas.create_text(
        155, 170, text="RM", fill="#61D9D0",
        font=("Arial", 40, "bold")
    )
    canvas.create_text(
        155, 355, text="Plan • Track • Save",
        fill=WHITE, font=("Arial", 11, "bold")
    )

    right = tk.Frame(outer, bg=WHITE)
    right.pack(side="left", fill="both", expand=True)

    tk.Label(
        right, text="Welcome Back",
        bg=WHITE, fg=NAVY,
        font=("Arial", 25, "bold")
    ).pack(anchor="w", padx=52, pady=(72, 5))

    tk.Label(
        right, text="Sign in to manage your student finances.",
        bg=WHITE, fg=MUTED, font=("Arial", 11)
    ).pack(anchor="w", padx=52, pady=(0, 28))

    form = tk.Frame(right, bg=WHITE)
    form.pack(fill="x", padx=52)

    login_username = tk.StringVar()
    login_password = tk.StringVar()

    w, _ = field(form, "Username", login_username)
    w.pack(fill="x", pady=7)

    w, _ = field(form, "Password", login_password, show="*")
    w.pack(fill="x", pady=7)

    make_button(
        right, "Login", login_user, primary=True
    ).pack(fill="x", padx=52, pady=(22, 12), ipady=2)

    tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=52, pady=10)

    make_button(
        right, "Create New Account", show_register
    ).pack(fill="x", padx=52, pady=8)

    tk.Label(
        right, text="A simple way to stay on top of your money.",
        bg=WHITE, fg=MUTED, font=("Arial", 9)
    ).pack(pady=(25, 0))


def show_register():
    global register_username, register_password, register_confirm

    clear_root()
    root.geometry("900x600")
    root.resizable(False, False)

    outer = tk.Frame(root, bg=BG)
    outer.pack(fill="both", expand=True)

    left = tk.Frame(outer, bg=NAVY, width=370)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    tk.Label(
        left, text="Start your\nmoney journey.",
        bg=NAVY, fg=WHITE,
        font=("Arial", 27, "bold"),
        justify="left"
    ).pack(anchor="w", padx=42, pady=(90, 12))

    tk.Label(
        left,
        text="Create one account and keep\nall your student finances organised.",
        bg=NAVY, fg="#61D9D0",
        font=("Arial", 11),
        justify="left"
    ).pack(anchor="w", padx=42)

    right = tk.Frame(outer, bg=WHITE)
    right.pack(side="left", fill="both", expand=True)

    tk.Label(
        right, text="Create Account",
        bg=WHITE, fg=NAVY,
        font=("Arial", 25, "bold")
    ).pack(anchor="w", padx=52, pady=(60, 5))

    tk.Label(
        right, text="Set up your student budget tracker account.",
        bg=WHITE, fg=MUTED, font=("Arial", 11)
    ).pack(anchor="w", padx=52, pady=(0, 25))

    form = tk.Frame(right, bg=WHITE)
    form.pack(fill="x", padx=52)

    register_username = tk.StringVar()
    register_password = tk.StringVar()
    register_confirm = tk.StringVar()

    for label, variable, show in [
        ("Username", register_username, None),
        ("Password", register_password, "*"),
        ("Confirm Password", register_confirm, "*")
    ]:
        w, _ = field(form, label, variable, show=show)
        w.pack(fill="x", pady=7)

    make_button(
        right, "Create Account", register_user, primary=True
    ).pack(fill="x", padx=52, pady=(22, 10), ipady=2)

    make_button(
        right, "Back to Login", show_login
    ).pack(fill="x", padx=52, pady=8)


# =========================================================
# MAIN APP SHELL
# =========================================================

def show_app():
    global content_frame, page_title_label, page_subtitle_label

    clear_root()
    root.geometry("1180x760")
    root.resizable(True, True)

    # Header
    header = tk.Frame(root, bg=NAVY, height=92)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header, text="Student Budget Tracker",
        bg=NAVY, fg=WHITE,
        font=("Arial", 23, "bold")
    ).pack(side="left", padx=28, pady=(17, 0), anchor="sw")

    user = get_username()

    tk.Label(
        header, text=f"Welcome back, {user}",
        bg=NAVY, fg="#61D9D0",
        font=("Arial", 10, "bold")
    ).pack(side="right", padx=30, pady=(28, 0))

    # Body
    body = tk.Frame(root, bg=BG)
    body.pack(fill="both", expand=True)

    # Sidebar
    sidebar = tk.Frame(body, bg=WHITE, width=190)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar, text="MENU", bg=WHITE, fg=MUTED,
        font=("Arial", 8, "bold")
    ).pack(anchor="w", padx=22, pady=(24, 12))

    menu = [
        ("Dashboard", show_dashboard),
        ("Budget Management", show_budget_page),
        ("Transactions", show_transactions_page),
        ("Reports", show_reports_page),
        ("Profile", show_profile_page)
    ]

    sidebar_buttons.clear()

    for text, command in menu:
        button = tk.Button(
            sidebar, text="  " + text,
            command=command,
            anchor="w",
            font=("Arial", 10, "bold"),
            bg=WHITE, fg=TEXT,
            activebackground=TEAL_LIGHT,
            activeforeground=TEAL_DARK,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12, pady=11
        )
        button.pack(fill="x", padx=12, pady=3)
        sidebar_buttons[text] = button

    tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=18)

    tk.Button(
        sidebar, text="  Logout",
        command=logout_user,
        anchor="w",
        font=("Arial", 10, "bold"),
        bg=WHITE, fg=RED,
        activebackground="#FFF0F1",
        relief="flat", bd=0, cursor="hand2",
        padx=12, pady=11
    ).pack(fill="x", padx=12)

    # Main area
    main = tk.Frame(body, bg=BG)
    main.pack(side="left", fill="both", expand=True)

    top = tk.Frame(main, bg=BG, height=78)
    top.pack(fill="x", padx=28)
    top.pack_propagate(False)

    page_title_label = tk.Label(
        top, text="", bg=BG, fg=TEXT,
        font=("Arial", 20, "bold")
    )
    page_title_label.pack(anchor="w", pady=(18, 0))

    page_subtitle_label = tk.Label(
        top, text="", bg=BG, fg=MUTED,
        font=("Arial", 9)
    )
    page_subtitle_label.pack(anchor="w", pady=(2, 0))

    content_frame = tk.Frame(main, bg=BG)
    content_frame.pack(fill="both", expand=True, padx=28, pady=(0, 20))

    show_dashboard()


def select_menu(name):
    for label, button in sidebar_buttons.items():
        if label == name:
            button.config(bg=TEAL, fg=WHITE)
        else:
            button.config(bg=WHITE, fg=TEXT)


def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():
    clear_content()
    set_page_header(
        "Dashboard",
        "A quick overview of your finances today."
    )
    select_menu("Dashboard")

    username = get_username()
    budget, income, expenses, balance = get_financial_summary()

    greeting = tk.Frame(content_frame, bg=BG)
    greeting.pack(fill="x", pady=(0, 16))

    tk.Label(
        greeting, text=f"Good to see you, {username}.",
        bg=BG, fg=TEXT, font=("Arial", 16, "bold")
    ).pack(side="left")

    tk.Label(
        greeting, text=date.today().strftime("%d %B %Y"),
        bg=BG, fg=MUTED, font=("Arial", 9)
    ).pack(side="right", pady=5)

    cards_frame = tk.Frame(content_frame, bg=BG)
    cards_frame.pack(fill="x")

    data = [
        ("Monthly Budget", f"RM {budget:,.2f}", TEAL),
        ("Total Income", f"RM {income:,.2f}", BLUE),
        ("Total Expenses", f"RM {expenses:,.2f}", RED),
        ("Current Balance", f"RM {balance:,.2f}", YELLOW)
    ]

    for title, value, accent in data:
        c, _ = card(cards_frame, title, value, accent)
        c.pack(side="left", fill="both", expand=True, padx=5)

    lower = tk.Frame(content_frame, bg=BG)
    lower.pack(fill="both", expand=True, pady=18)

    recent = tk.Frame(
        lower, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    recent.pack(side="left", fill="both", expand=True, padx=(0, 8))

    tk.Label(
        recent, text="Recent Transactions",
        bg=WHITE, fg=TEXT,
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=16, pady=(14, 8))

    show_recent_transactions(recent)

    side = tk.Frame(
        lower, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1,
        width=300
    )
    side.pack(side="left", fill="y", padx=(8, 0))
    side.pack_propagate(False)

    tk.Label(
        side, text="Budget Progress",
        bg=WHITE, fg=TEXT,
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=16, pady=(14, 12))

    spent = expenses
    percentage = (spent / budget * 100) if budget else 0
    percentage = min(percentage, 100)

    tk.Label(
        side, text=f"RM {spent:,.2f} spent",
        bg=WHITE, fg=TEXT, font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=16)

    tk.Label(
        side, text=f"of RM {budget:,.2f} monthly budget",
        bg=WHITE, fg=MUTED, font=("Arial", 9)
    ).pack(anchor="w", padx=16, pady=(2, 12))

    progress = ttk.Progressbar(
        side, orient="horizontal",
        length=240, mode="determinate"
    )
    progress["value"] = percentage
    progress.pack(padx=16, fill="x")

    tk.Label(
        side, text=f"{percentage:.0f}% used",
        bg=WHITE, fg=MUTED, font=("Arial", 9)
    ).pack(anchor="e", padx=16, pady=6)

    make_button(
        side, "Add Expense", show_budget_page, primary=True
    ).pack(fill="x", padx=16, pady=(18, 7))

    make_button(
        side, "View Reports", show_reports_page
    ).pack(fill="x", padx=16)


def show_recent_transactions(parent):
    connection = finance_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT date, category, type, amount
        FROM Transactions
        WHERE user_id = ?
        ORDER BY date DESC, transaction_id DESC
        LIMIT 6
    """, (logged_in_user_id,))
    rows = cursor.fetchall()
    connection.close()

    if not rows:
        tk.Label(
            parent,
            text="No transactions yet. Add your first income or expense.",
            bg=WHITE, fg=MUTED, font=("Arial", 9)
        ).pack(anchor="w", padx=16, pady=18)
        return

    table = tk.Frame(parent, bg=WHITE)
    table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    headers = ["Date", "Category", "Type", "Amount"]
    for col, header in enumerate(headers):
        tk.Label(
            table, text=header, bg="#F5F8FA", fg=MUTED,
            font=("Arial", 8, "bold"), anchor="w"
        ).grid(row=0, column=col, sticky="ew", padx=2, pady=2)

    for i, row in enumerate(rows, start=1):
        dt, category, kind, amount = row
        amount_text = ("+ " if kind == "Income" else "- ") + f"RM {amount:.2f}"
        amount_fg = GREEN if kind == "Income" else RED

        values = [dt, category, kind, amount_text]
        for col, value in enumerate(values):
            tk.Label(
                table, text=value, bg=WHITE,
                fg=amount_fg if col == 3 else TEXT,
                font=("Arial", 8, "bold" if col == 3 else "normal"),
                anchor="w"
            ).grid(row=i, column=col, sticky="ew", padx=5, pady=5)

    for col in range(4):
        table.columnconfigure(col, weight=1)


# =========================================================
# BUDGET MANAGEMENT PAGE
# =========================================================

def save_budget():
    value = budget_var.get().strip()

    try:
        amount = float(value)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid budget", "Enter a valid amount greater than RM 0.")
        return

    connection = finance_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT budget_id FROM Budget WHERE user_id = ?",
        (logged_in_user_id,)
    )
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE Budget SET monthly_budget = ? WHERE user_id = ?",
            (amount, logged_in_user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO Budget(user_id, monthly_budget) VALUES (?, ?)",
            (logged_in_user_id, amount)
        )

    connection.commit()
    connection.close()
    budget_var.set("")
    messagebox.showinfo("Budget saved", f"Monthly budget set to RM {amount:.2f}.")
    show_budget_page()


def add_income():
    add_transaction("Income")


def add_expense():
    add_transaction("Expense")


def add_transaction(kind):
    variable = income_amount_var if kind == "Income" else expense_amount_var
    category_var = income_category_var if kind == "Income" else expense_category_var

    try:
        amount = float(variable.get().strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid amount", f"Enter a valid {kind.lower()} amount.")
        return

    connection = finance_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Transactions(user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        logged_in_user_id,
        amount,
        category_var.get(),
        kind,
        transaction_date_var.get().strip() or date.today().isoformat()
    ))
    connection.commit()
    connection.close()

    variable.set("")
    messagebox.showinfo(
        f"{kind} added",
        f"{kind} of RM {amount:.2f} has been recorded."
    )
    show_budget_page()


def show_budget_page():
    clear_content()
    set_page_header(
        "Budget Management",
        "Manage your budget, income and expenses in one place."
    )
    select_menu("Budget Management")

    top = tk.Frame(content_frame, bg=BG)
    top.pack(fill="x", pady=(0, 14))

    budget, income, expenses, balance = get_financial_summary()

    for title, value, accent in [
        ("Budget", f"RM {budget:,.2f}", TEAL),
        ("Income", f"RM {income:,.2f}", BLUE),
        ("Expenses", f"RM {expenses:,.2f}", RED),
        ("Balance", f"RM {balance:,.2f}", YELLOW)
    ]:
        c, _ = card(top, title, value, accent)
        c.pack(side="left", fill="both", expand=True, padx=5)

    forms = tk.Frame(content_frame, bg=BG)
    forms.pack(fill="both", expand=True)

    budget_box = make_form_card(forms, "Budget & Income", "Set your monthly budget and record income.")
    budget_box.pack(side="left", fill="both", expand=True, padx=5)

    w, _ = field(budget_box, "Monthly Budget (RM)", budget_var)
    w.pack(fill="x", padx=18, pady=(14, 8))
    make_button(budget_box, "Save Budget", save_budget, primary=True).pack(fill="x", padx=18, pady=5)

    ttk.Separator(budget_box, orient="horizontal").pack(fill="x", padx=18, pady=14)

    w, _ = field(budget_box, "Income Amount (RM)", income_amount_var)
    w.pack(fill="x", padx=18, pady=6)

    tk.Label(
        budget_box, text="Income Category",
        bg=WHITE, fg=TEXT, font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=18, pady=(4, 5))

    income_menu = ttk.Combobox(
        budget_box, textvariable=income_category_var,
        values=["Allowance", "Parents", "Part-Time Job", "Freelance Work",
                "Scholarship", "Gift", "Savings", "Other"],
        state="readonly"
    )
    income_menu.pack(fill="x", padx=18)
    make_button(budget_box, "Add Income", add_income).pack(fill="x", padx=18, pady=12)

    expense_box = make_form_card(forms, "Expense", "Record spending and keep your balance updated.")
    expense_box.pack(side="left", fill="both", expand=True, padx=5)

    w, _ = field(expense_box, "Expense Amount (RM)", expense_amount_var)
    w.pack(fill="x", padx=18, pady=(14, 8))

    tk.Label(
        expense_box, text="Expense Category",
        bg=WHITE, fg=TEXT, font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=18, pady=(4, 5))

    expense_menu = ttk.Combobox(
        expense_box, textvariable=expense_category_var,
        values=["Food", "Transport", "Shopping", "Bills",
                "Entertainment", "Education", "Health", "Other"],
        state="readonly"
    )
    expense_menu.pack(fill="x", padx=18)

    w, _ = field(expense_box, "Date (YYYY-MM-DD)", transaction_date_var)
    w.pack(fill="x", padx=18, pady=12)

    make_button(expense_box, "Add Expense", add_expense, primary=True).pack(
        fill="x", padx=18, pady=5
    )

    make_button(
        expense_box, "Check Current Balance",
        lambda: messagebox.showinfo(
            "Current Balance",
            f"Income: RM {income:,.2f}\n"
            f"Expenses: RM {expenses:,.2f}\n"
            f"Balance: RM {balance:,.2f}"
        )
    ).pack(fill="x", padx=18, pady=7)


def make_form_card(parent, title, subtitle):
    box = tk.Frame(
        parent, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    tk.Label(
        box, text=title, bg=WHITE, fg=TEXT,
        font=("Arial", 13, "bold")
    ).pack(anchor="w", padx=18, pady=(16, 2))
    tk.Label(
        box, text=subtitle, bg=WHITE, fg=MUTED,
        font=("Arial", 8)
    ).pack(anchor="w", padx=18)
    return box


# =========================================================
# TRANSACTIONS PAGE
# =========================================================

def show_transactions_page():
    clear_content()
    set_page_header(
        "Transactions",
        "Review and manage your recorded income and expenses."
    )
    select_menu("Transactions")

    box = tk.Frame(
        content_frame, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    box.pack(fill="both", expand=True)

    tk.Label(
        box, text="Transaction History",
        bg=WHITE, fg=TEXT, font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=18, pady=(16, 10))

    tree = ttk.Treeview(
        box,
        columns=("date", "category", "type", "amount"),
        show="headings"
    )

    for col, heading, width in [
        ("date", "Date", 150),
        ("category", "Category", 220),
        ("type", "Type", 150),
        ("amount", "Amount", 180)
    ]:
        tree.heading(col, text=heading)
        tree.column(col, width=width, anchor="w")

    tree.pack(fill="both", expand=True, padx=18, pady=(0, 15))

    connection = finance_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT transaction_id, date, category, type, amount
        FROM Transactions
        WHERE user_id = ?
        ORDER BY date DESC, transaction_id DESC
    """, (logged_in_user_id,))
    rows = cursor.fetchall()
    connection.close()

    for transaction_id, dt, category, kind, amount in rows:
        tree.insert(
            "", "end", iid=str(transaction_id),
            values=(dt, category, kind, f"RM {amount:.2f}")
        )

    actions = tk.Frame(box, bg=WHITE)
    actions.pack(fill="x", padx=18, pady=(0, 15))

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select transaction", "Choose a transaction first.")
            return

        if not messagebox.askyesno(
            "Delete transaction",
            "Delete the selected transaction?"
        ):
            return

        connection = finance_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM Transactions WHERE transaction_id = ? AND user_id = ?",
            (int(selected[0]), logged_in_user_id)
        )
        connection.commit()
        connection.close()
        show_transactions_page()

    make_button(
        actions, "Delete Selected", delete_selected
    ).pack(side="left")

    make_button(
        actions, "Add New Transaction", show_budget_page, primary=True
    ).pack(side="right")


# =========================================================
# REPORTS
# =========================================================

def show_reports_page():
    clear_content()
    set_page_header(
        "Reports & Analytics",
        "Understand where your money is going."
    )
    select_menu("Reports")

    budget, income, expenses, balance = get_financial_summary()

    cards_frame = tk.Frame(content_frame, bg=BG)
    cards_frame.pack(fill="x")

    for title, value, accent in [
        ("Total Income", f"RM {income:,.2f}", BLUE),
        ("Total Expenses", f"RM {expenses:,.2f}", RED),
        ("Current Balance", f"RM {balance:,.2f}", TEAL)
    ]:
        c, _ = card(cards_frame, title, value, accent)
        c.pack(side="left", fill="both", expand=True, padx=5)

    analytics = tk.Frame(content_frame, bg=BG)
    analytics.pack(fill="both", expand=True, pady=18)

    left = make_form_card(
        analytics, "Spending by Category",
        "See which categories take the biggest share."
    )
    left.pack(side="left", fill="both", expand=True, padx=5)

    connection = finance_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT category, COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE user_id = ? AND type = 'Expense'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, (logged_in_user_id,))
    category_rows = cursor.fetchall()
    connection.close()

    if category_rows:
        for category, total in category_rows:
            row = tk.Frame(left, bg=WHITE)
            row.pack(fill="x", padx=18, pady=6)
            tk.Label(
                row, text=category, bg=WHITE, fg=TEXT,
                font=("Arial", 9, "bold")
            ).pack(side="left")
            tk.Label(
                row, text=f"RM {total:.2f}", bg=WHITE, fg=TEXT,
                font=("Arial", 9)
            ).pack(side="right")
    else:
        tk.Label(
            left, text="No expense data yet.",
            bg=WHITE, fg=MUTED, font=("Arial", 9)
        ).pack(anchor="w", padx=18, pady=18)

    right = make_form_card(
        analytics, "Quick Reports",
        "Useful summaries for your coursework demonstration."
    )
    right.pack(side="left", fill="both", expand=True, padx=5)

    def financial_report():
        remaining_budget = budget - expenses
        messagebox.showinfo(
            "Financial Report",
            f"Monthly Budget: RM {budget:.2f}\n"
            f"Total Income: RM {income:.2f}\n"
            f"Total Expenses: RM {expenses:.2f}\n"
            f"Current Balance: RM {balance:.2f}\n"
            f"Remaining Budget: RM {remaining_budget:.2f}"
        )

    def budget_warning():
        if budget <= 0:
            messagebox.showinfo("Budget Status", "Set a monthly budget to see your budget status.")
        elif expenses > budget:
            messagebox.showwarning(
                "Budget Warning",
                f"You are RM {expenses - budget:.2f} over your monthly budget."
            )
        else:
            messagebox.showinfo(
                "Budget Status",
                f"RM {budget - expenses:.2f} remains in your monthly budget."
            )

    make_button(
        right, "Generate Financial Report",
        financial_report, primary=True
    ).pack(fill="x", padx=18, pady=(18, 7))

    make_button(
        right, "Check Budget Status",
        budget_warning
    ).pack(fill="x", padx=18, pady=7)

    make_button(
        right, "View Transaction History",
        show_transactions_page
    ).pack(fill="x", padx=18, pady=7)


# =========================================================
# PROFILE
# =========================================================

def show_profile_page():
    global profile_photo

    clear_content()
    set_page_header(
        "Profile",
        "Manage your account information."
    )
    select_menu("Profile")

    layout = tk.Frame(content_frame, bg=BG)
    layout.pack(fill="both", expand=True)

    profile_card = tk.Frame(
        layout, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1,
        width=340
    )
    profile_card.pack(side="left", fill="y", padx=(0, 10))
    profile_card.pack_propagate(False)

    avatar = tk.Label(
        profile_card,
        text=get_username()[0].upper(),
        bg=NAVY_2, fg=WHITE,
        font=("Arial", 38, "bold"),
        width=4, height=2
    )
    avatar.pack(pady=(35, 15))

    tk.Label(
        profile_card, text=get_username(),
        bg=WHITE, fg=TEXT,
        font=("Arial", 16, "bold")
    ).pack()

    tk.Label(
        profile_card, text="Student Budget Tracker",
        bg=WHITE, fg=MUTED,
        font=("Arial", 9)
    ).pack(pady=3)

    def choose_photo():
        global profile_photo, profile_photo_path
        path = filedialog.askopenfilename(
            title="Choose profile picture",
            filetypes=[
                ("PNG images", "*.png"),
                ("GIF images", "*.gif"),
                ("JPEG images", "*.jpg;*.jpeg")
            ]
        )
        if not path:
            return

        profile_photo_path = path

        try:
            if PIL_AVAILABLE:
                image = Image.open(path)
                image = image.resize((110, 110))
                profile_photo = ImageTk.PhotoImage(image)
            else:
                profile_photo = tk.PhotoImage(file=path)
            avatar.config(image=profile_photo, text="")
        except Exception:
            messagebox.showerror(
                "Picture error",
                "The picture could not be loaded. PNG is recommended."
            )

    make_button(
        profile_card, "Change Profile Picture", choose_photo
    ).pack(fill="x", padx=28, pady=(22, 5))

    tk.Label(
        profile_card,
        text="PNG recommended",
        bg=WHITE, fg=MUTED, font=("Arial", 8)
    ).pack()

    account = tk.Frame(
        layout, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    account.pack(side="left", fill="both", expand=True, padx=(10, 0))

    tk.Label(
        account, text="Account Information",
        bg=WHITE, fg=TEXT,
        font=("Arial", 13, "bold")
    ).pack(anchor="w", padx=24, pady=(22, 4))

    tk.Label(
        account,
        text="Update your username or password below.",
        bg=WHITE, fg=MUTED, font=("Arial", 9)
    ).pack(anchor="w", padx=24, pady=(0, 18))

    w, _ = field(account, "Username", profile_username_var)
    w.pack(fill="x", padx=24, pady=7)

    w, _ = field(account, "New Password", profile_password_var, show="*")
    w.pack(fill="x", padx=24, pady=7)

    w, _ = field(account, "Confirm New Password", profile_confirm_var, show="*")
    w.pack(fill="x", padx=24, pady=7)

    profile_username_var.set(get_username())
    profile_password_var.set("")
    profile_confirm_var.set("")

    def save_profile():
        global logged_in_user_id

        username = profile_username_var.get().strip()
        password = profile_password_var.get()
        confirm = profile_confirm_var.get()

        if not username:
            messagebox.showwarning("Invalid username", "Username cannot be empty.")
            return

        if password != confirm:
            messagebox.showwarning("Password mismatch", "The passwords do not match.")
            return

        connection = sqlite3.connect(USER_DB)
        cursor = connection.cursor()

        try:
            if password:
                cursor.execute(
                    "UPDATE users SET username = ?, password = ? WHERE user_id = ?",
                    (username, password, logged_in_user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = ? WHERE user_id = ?",
                    (username, logged_in_user_id)
                )

            connection.commit()
            messagebox.showinfo("Profile updated", "Your profile has been updated.")
            show_app()
        except sqlite3.IntegrityError:
            messagebox.showerror("Username unavailable", "That username is already in use.")
        finally:
            connection.close()

    make_button(
        account, "Save Changes", save_profile, primary=True
    ).pack(fill="x", padx=24, pady=(20, 7))

    make_button(
        account, "Back to Dashboard", show_dashboard
    ).pack(fill="x", padx=24, pady=5)


# =========================================================
# LOGOUT / START
# =========================================================

def logout_user():
    global logged_in_user_id
    logged_in_user_id = None
    show_login()


create_databases()
show_login()
root.mainloop()
