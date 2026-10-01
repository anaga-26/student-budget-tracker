import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import date
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

    # =====================================================
    # WINDOW
    # =====================================================

    root.geometry("1100x700")
    root.minsize(1000, 650)
    root.resizable(True, True)

    # =====================================================
    # COLOUR PALETTE
    # =====================================================

    login_bg = "#F4F8FA"
    login_navy = "#102A43"
    login_navy_light = "#173E5F"
    login_teal = "#19A999"
    login_teal_dark = "#128477"
    login_text = "#19324D"
    login_muted = "#7A8A9A"
    white = "#FFFFFF"
    input_bg = "#F8FAFC"
    border = "#DCE6ED"

    # =====================================================
    # MAIN CONTAINER
    # =====================================================

    outer = tk.Frame(
        root,
        bg=login_bg
    )
    outer.pack(
        fill="both",
        expand=True
    )

    # =====================================================
    # LEFT BRANDING PANEL
    # =====================================================

    left = tk.Frame(
        outer,
        bg=login_navy,
        width=500
    )

    left.pack(
        side="left",
        fill="y"
    )

    left.pack_propagate(False)

    # =====================================================
    # SUBTLE DECORATION
    # =====================================================

    decoration = tk.Canvas(
        left,
        bg=login_navy,
        highlightthickness=0
    )

    decoration.place(
        relx=0,
        rely=0,
        relwidth=1,
        relheight=1
    )

    # Soft decorative shapes
    decoration.create_oval(
        -180, 500, 250, 930,
        fill="#153957",
        outline=""
    )

    decoration.create_oval(
        300, -150, 570, 120,
        fill="#153957",
        outline=""
    )

    decoration.create_oval(
        315, 500, 540, 725,
        fill="#174568",
        outline=""
    )

    # =====================================================
    # BRAND CONTENT
    # =====================================================

    brand = tk.Frame(
        left,
        bg=login_navy
    )

    brand.pack(
        fill="x",
        padx=45,
        pady=(70, 0)
    )

    # Main application name
    tk.Label(
        brand,
        text="STUDENT BUDGET TRACKER",
        bg=login_navy,
        fg=white,
        font=("Arial", 19, "bold"),
        anchor="w"
    ).pack(
        anchor="w"
    )

    # Accent line
    tk.Frame(
        brand,
        bg=login_teal,
        height=4,
        width=75
    ).pack(
        anchor="w",
        pady=(15, 18)
    )

    # Short description
    tk.Label(
        brand,
        text="A simple and organised way\nto manage your student finances.",
        bg=login_navy,
        fg="#B9C9D9",
        font=("Arial", 11),
        justify="left",
        anchor="w"
    ).pack(
        anchor="w"
    )

    # =====================================================
    # SIMPLE ILLUSTRATION / MONEY VISUAL
    # =====================================================

    visual = tk.Frame(
        left,
        bg=login_navy
    )

    visual.pack(
        fill="both",
        expand=True,
        padx=55,
        pady=(40, 55)
    )

    canvas = tk.Canvas(
        visual,
        bg=login_navy,
        highlightthickness=0
    )

    canvas.pack(
        fill="both",
        expand=True
    )

    # Main soft circle
    canvas.create_oval(
        55, 75,
        285, 305,
        fill="#173E5F",
        outline=""
    )

    # Small decorative circle
    canvas.create_oval(
        220, 185,
        330, 295,
        fill="#1B4B70",
        outline=""
    )
    
    canvas.create_rectangle(
        100, 145,
        275, 255,
        fill="#FFFFFF",
        outline=""
    )

    canvas.create_rectangle(
        95, 160,
        290, 195,
        fill="#19A999",
        outline=""
    )

    # Card details
    canvas.create_oval(
        115, 215,
        140, 240,
        fill="#D9F5F1",
        outline=""
    )

    canvas.create_rectangle(
        155, 215,
        235, 222,
        fill="#D8E5EC",
        outline=""
    )

    canvas.create_rectangle(
        155, 232,
        210, 239,
        fill="#D8E5EC",
        outline=""
    )

    # Decorative coins
    canvas.create_oval(
        260, 120,
        305, 165,
        fill="#66DED3",
        outline=""
    )

    canvas.create_text(
        282,
        142,
        text="RM",
        fill=login_navy,
        font=("Arial", 11, "bold")
    )

    # Bottom tagline
    canvas.create_text(
        170,
        350,
        text="Plan. Track. Save.",
        fill=white,
        font=("Arial", 17, "bold")
    )

    canvas.create_text(
        170,
        378,
        text="Built for students who want\nbetter control of their money.",
        fill="#9FB5C8",
        font=("Arial", 9),
        justify="center"
    )

    # =====================================================
    # RIGHT SIDE
    # =====================================================

    right = tk.Frame(
        outer,
        bg=login_bg
    )

    right.pack(
        side="left",
        fill="both",
        expand=True
    )

    # =====================================================
    # LOGIN CARD
    # =====================================================

    login_card_frame = tk.Frame(
        right,
        bg=white,
        highlightbackground=border,
        highlightthickness=1
    )

    login_card_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=500,
        height=555
    )

    # =====================================================
    # HEADER
    # =====================================================

    tk.Label(
        login_card_frame,
        text="Welcome",
        bg=white,
        fg=login_text,
        font=("Arial", 27, "bold")
    ).pack(
        anchor="w",
        padx=55,
        pady=(38, 5)
    )

    tk.Label(
        login_card_frame,
        text="Sign in to continue to your dashboard.",
        bg=white,
        fg=login_muted,
        font=("Arial", 10)
    ).pack(
        anchor="w",
        padx=55
    )

    # =====================================================
    # FORM
    # =====================================================

    form = tk.Frame(
        login_card_frame,
        bg=white
    )

    form.pack(
        fill="x",
        padx=55,
        pady=(26, 0)
    )

    login_username = tk.StringVar()
    login_password = tk.StringVar()

    # -----------------------------------------------------
    # USERNAME
    # -----------------------------------------------------

    tk.Label(
        form,
        text="Username",
        bg=white,
        fg=login_text,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        pady=(0, 8)
    )

    username_entry = tk.Entry(
        form,
        textvariable=login_username,
        font=("Arial", 11),
        bg=input_bg,
        fg=login_text,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=login_teal
    )

    username_entry.pack(
        fill="x",
        ipady=11
    )

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    tk.Label(
        form,
        text="Password",
        bg=white,
        fg=login_text,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        pady=(20, 8)
    )

    password_entry = tk.Entry(
        form,
        textvariable=login_password,
        font=("Arial", 11),
        bg=input_bg,
        fg=login_text,
        relief="flat",
        bd=0,
        show="*",
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=login_teal
    )

    password_entry.pack(
        fill="x",
        ipady=11
    )

    # =====================================================
    # LOGIN BUTTON
    # =====================================================

    login_button = tk.Button(
        login_card_frame,
        text="Sign In",
        command=login_user,
        bg=login_teal,
        fg=white,
        activebackground=login_teal_dark,
        activeforeground=white,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Arial", 10, "bold")
    )

    login_button.pack(
        fill="x",
        padx=48,
        pady=(20, 15),
        ipady=10
    )

    # =====================================================
    # DIVIDER
    # =====================================================

    divider_area = tk.Frame(
        login_card_frame,
        bg=white
    )

    divider_area.pack(
        fill="x",
        padx=55,
        pady=(0, 17)
    )

    tk.Frame(
        divider_area,
        bg=border,
        height=1
    ).pack(
        side="left",
        fill="x",
        expand=True
    )

    tk.Label(
        divider_area,
        text="  or  ",
        bg=white,
        fg=login_muted,
        font=("Arial", 8)
    ).pack(
        side="left"
    )

    tk.Frame(
        divider_area,
        bg=border,
        height=1
    ).pack(
        side="left",
        fill="x",
        expand=True
    )

    # =====================================================
    # CREATE ACCOUNT
    # =====================================================

    register_button = tk.Button(
        login_card_frame,
        text="Create New Account",
        command=show_register,
        bg=white,
        fg=login_teal_dark,
        activebackground="#EAF8F6",
        activeforeground=login_teal_dark,
        relief="solid",
        bd=1,
        cursor="hand2",
        font=("Arial", 9, "bold")
    )

    register_button.pack(
        fill="x",
        padx=55,
        pady=(0, 10),
        ipady=9
    )

    # =====================================================
    # FOOTER
    # =====================================================

    tk.Label(
        login_card_frame,
        text="Manage your money. Build better habits.",
        bg=white,
        fg=login_muted,
        font=("Arial", 8)
    ).pack(
        pady=(8, 0)
    )

    # =====================================================
    # START WITH USERNAME FIELD
    # =====================================================

    username_entry.focus_set()

def show_register():
    global register_username, register_password, register_confirm

    clear_root()

    # =====================================================
    # WINDOW
    # =====================================================

    root.geometry("1100x700")
    root.minsize(1000, 650)
    root.resizable(True, True)

    # =====================================================
    # COLOUR PALETTE
    # =====================================================

    register_bg = "#F4F8FA"
    register_navy = "#102A43"
    register_teal = "#19A999"
    register_teal_dark = "#128477"
    register_text = "#19324D"
    register_muted = "#7A8A9A"
    white = "#FFFFFF"
    input_bg = "#F8FAFC"
    border = "#DCE6ED"

    # =====================================================
    # MAIN CONTAINER
    # =====================================================

    outer = tk.Frame(
        root,
        bg=register_bg
    )

    outer.pack(
        fill="both",
        expand=True
    )

    # =====================================================
    # LEFT BRANDING PANEL
    # =====================================================

    left = tk.Frame(
        outer,
        bg=register_navy,
        width=500
    )

    left.pack(
        side="left",
        fill="y"
    )

    left.pack_propagate(False)

    # =====================================================
    # SUBTLE BACKGROUND DECORATION
    # =====================================================

    decoration = tk.Canvas(
        left,
        bg=register_navy,
        highlightthickness=0
    )

    decoration.place(
        relx=0,
        rely=0,
        relwidth=1,
        relheight=1
    )

    decoration.create_oval(
        -180, 500, 250, 930,
        fill="#153957",
        outline=""
    )

    decoration.create_oval(
        300, -150, 570, 120,
        fill="#153957",
        outline=""
    )

    decoration.create_oval(
        315, 500, 540, 725,
        fill="#174568",
        outline=""
    )

    # =====================================================
    # BRANDING
    # =====================================================

    brand = tk.Frame(
        left,
        bg=register_navy
    )

    brand.pack(
        fill="x",
        padx=45,
        pady=(70, 0)
    )

    tk.Label(
        brand,
        text="STUDENT BUDGET TRACKER",
        bg=register_navy,
        fg=white,
        font=("Arial", 19, "bold"),
        anchor="w"
    ).pack(
        anchor="w"
    )

    tk.Frame(
        brand,
        bg=register_teal,
        height=4,
        width=75
    ).pack(
        anchor="w",
        pady=(15, 18)
    )

    tk.Label(
        brand,
        text="Create your account and start\norganising your student finances.",
        bg=register_navy,
        fg="#B9C9D9",
        font=("Arial", 11),
        justify="left",
        anchor="w"
    ).pack(
        anchor="w"
    )

    # =====================================================
    # SIMPLE ILLUSTRATION
    # =====================================================

    visual = tk.Frame(
        left,
        bg=register_navy
    )

    visual.pack(
        fill="both",
        expand=True,
        padx=55,
        pady=(35, 45)
    )

    canvas = tk.Canvas(
        visual,
        bg=register_navy,
        highlightthickness=0
    )

    canvas.pack(
        fill="both",
        expand=True
    )

    # Main circle
    canvas.create_oval(
        55, 55,
        285, 285,
        fill="#173E5F",
        outline=""
    )

    # User/account card
    canvas.create_rectangle(
        105, 105,
        275, 225,
        fill=white,
        outline=""
    )

    # Teal header
    canvas.create_rectangle(
        105, 105,
        275, 140,
        fill=register_teal,
        outline=""
    )

    # Profile circle
    canvas.create_oval(
        125, 155,
        160, 190,
        fill="#D9F5F1",
        outline=""
    )

    # Profile details
    canvas.create_rectangle(
        175, 158,
        245, 165,
        fill="#D8E5EC",
        outline=""
    )

    canvas.create_rectangle(
        175, 175,
        230, 182,
        fill="#D8E5EC",
        outline=""
    )

    # Small decorative check
    canvas.create_oval(
        250, 90,
        295, 135,
        fill="#66DED3",
        outline=""
    )

    canvas.create_text(
        272,
        112,
        text="✓",
        fill=register_navy,
        font=("Arial", 14, "bold")
    )

    canvas.create_text(
        170,
        335,
        text="Start organised.",
        fill=white,
        font=("Arial", 17, "bold")
    )

    canvas.create_text(
        170,
        365,
        text="Create your account and\nkeep your finances in one place.",
        fill="#9FB5C8",
        font=("Arial", 9),
        justify="center"
    )

    # =====================================================
    # RIGHT SIDE
    # =====================================================

    right = tk.Frame(
        outer,
        bg=register_bg
    )

    right.pack(
        side="left",
        fill="both",
        expand=True
    )

    # =====================================================
    # REGISTER CARD
    # =====================================================

    register_card = tk.Frame(
        right,
        bg=white,
        highlightbackground=border,
        highlightthickness=1
    )

    register_card.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=500,
        height=570
    )

    # =====================================================
    # HEADER
    # =====================================================

    tk.Label(
        register_card,
        text="Create Account",
        bg=white,
        fg=register_text,
        font=("Arial", 27, "bold")
    ).pack(
        anchor="w",
        padx=55,
        pady=(42, 5)
    )

    tk.Label(
        register_card,
        text="Create your account to get started.",
        bg=white,
        fg=register_muted,
        font=("Arial", 10)
    ).pack(
        anchor="w",
        padx=55
    )

    # =====================================================
    # FORM
    # =====================================================

    form = tk.Frame(
        register_card,
        bg=white
    )

    form.pack(
        fill="x",
        padx=55,
        pady=(27, 0)
    )

    register_username = tk.StringVar()
    register_password = tk.StringVar()
    register_confirm = tk.StringVar()

    # -----------------------------------------------------
    # USERNAME
    # -----------------------------------------------------

    tk.Label(
        form,
        text="Username",
        bg=white,
        fg=register_text,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        pady=(0, 7)
    )

    username_entry = tk.Entry(
        form,
        textvariable=register_username,
        font=("Arial", 11),
        bg=input_bg,
        fg=register_text,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=register_teal
    )

    username_entry.pack(
        fill="x",
        ipady=10
    )

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    tk.Label(
        form,
        text="Password",
        bg=white,
        fg=register_text,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        pady=(17, 7)
    )

    password_entry = tk.Entry(
        form,
        textvariable=register_password,
        font=("Arial", 11),
        bg=input_bg,
        fg=register_text,
        relief="flat",
        bd=0,
        show="*",
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=register_teal
    )

    password_entry.pack(
        fill="x",
        ipady=10
    )

    # -----------------------------------------------------
    # CONFIRM PASSWORD
    # -----------------------------------------------------

    tk.Label(
        form,
        text="Confirm Password",
        bg=white,
        fg=register_text,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        pady=(17, 7)
    )

    confirm_entry = tk.Entry(
        form,
        textvariable=register_confirm,
        font=("Arial", 11),
        bg=input_bg,
        fg=register_text,
        relief="flat",
        bd=0,
        show="*",
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=register_teal
    )

    confirm_entry.pack(
        fill="x",
        ipady=10
    )

    # =====================================================
    # CREATE ACCOUNT BUTTON
    # =====================================================

    create_button = tk.Button(
        register_card,
        text="Create Account",
        command=register_user,
        bg=register_teal,
        fg=white,
        activebackground=register_teal_dark,
        activeforeground=white,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Arial", 10, "bold")
    )

    create_button.pack(
        fill="x",
        padx=55,
        pady=(25, 14),
        ipady=10
    )

    # =====================================================
    # DIVIDER
    # =====================================================

    divider_area = tk.Frame(
        register_card,
        bg=white
    )

    divider_area.pack(
        fill="x",
        padx=55,
        pady=(0, 14)
    )

    tk.Frame(
        divider_area,
        bg=border,
        height=1
    ).pack(
        side="left",
        fill="x",
        expand=True
    )

    tk.Label(
        divider_area,
        text="  already have an account?  ",
        bg=white,
        fg=register_muted,
        font=("Arial", 8)
    ).pack(
        side="left"
    )

    tk.Frame(
        divider_area,
        bg=border,
        height=1
    ).pack(
        side="left",
        fill="x",
        expand=True
    )

    # =====================================================
    # BACK TO LOGIN
    # =====================================================

    back_button = tk.Button(
        register_card,
        text="Back to Login",
        command=show_login,
        bg=white,
        fg=register_teal_dark,
        activebackground="#EAF8F6",
        activeforeground=register_teal_dark,
        relief="solid",
        bd=1,
        cursor="hand2",
        font=("Arial", 9, "bold")
    )

    back_button.pack(
        fill="x",
        padx=55,
        pady=(0, 10),
        ipady=9
    )

    # =====================================================
    # FOOTER
    # =====================================================

    tk.Label(
        register_card,
        text="Manage your money. Build better habits.",
        bg=white,
        fg=register_muted,
        font=("Arial", 8)
    ).pack(
        pady=(5, 0)
    )

    username_entry.focus_set()

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
        "A simple overview of your student finances."
    )
    select_menu("Dashboard")

    username = get_username()
    budget, income, expenses, balance = get_financial_summary()

    # =====================================================
    # WELCOME SECTION
    # =====================================================

    welcome = tk.Frame(
        content_frame,
        bg=BG
    )
    welcome.pack(
        fill="x",
        pady=(0, 22)
    )

    tk.Label(
        welcome,
        text=f"Good to see you, {username}.",
        bg=BG,
        fg=TEXT,
        font=("Arial", 18, "bold")
    ).pack(
        side="left"
    )

    tk.Label(
        welcome,
        text=date.today().strftime("%d %B %Y"),
        bg=BG,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(
        side="right",
        pady=5
    )

    # =====================================================
    # FINANCIAL SUMMARY CARDS
    # =====================================================

    cards_frame = tk.Frame(
        content_frame,
        bg=BG
    )
    cards_frame.pack(
        fill="x",
        pady=(0, 20)
    )

    summary_data = [
        ("MONTHLY BUDGET", f"RM {budget:,.2f}", TEAL),
        ("TOTAL INCOME", f"RM {income:,.2f}", BLUE),
        ("TOTAL EXPENSES", f"RM {expenses:,.2f}", RED),
        ("CURRENT BALANCE", f"RM {balance:,.2f}", YELLOW)
    ]

    for title, value, accent in summary_data:

        card_frame = tk.Frame(
            cards_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        # Accent line
        tk.Frame(
            card_frame,
            bg=accent,
            height=4
        ).pack(
            fill="x"
        )

        inner = tk.Frame(
            card_frame,
            bg=WHITE
        )

        inner.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=15
        )

        tk.Label(
            inner,
            text=title,
            bg=WHITE,
            fg=MUTED,
            font=("Arial", 8, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            inner,
            text=value,
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 17, "bold")
        ).pack(
            anchor="w",
            pady=(8, 2)
        )

    # =====================================================
    # LOWER SECTION
    # =====================================================

    lower = tk.Frame(
        content_frame,
        bg=BG
    )

    lower.pack(
        fill="both",
        expand=True
    )

    # =====================================================
    # RECENT TRANSACTIONS
    # =====================================================

    recent = tk.Frame(
        lower,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    recent.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 10)
    )

    recent_header = tk.Frame(
        recent,
        bg=WHITE
    )

    recent_header.pack(
        fill="x",
        padx=18,
        pady=(17, 10)
    )

    tk.Label(
        recent_header,
        text="Recent Transactions",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 12, "bold")
    ).pack(
        side="left"
    )

    tk.Label(
        recent_header,
        text="Latest activity",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8)
    ).pack(
        side="right",
        pady=2
    )

    show_recent_transactions(recent)

    # =====================================================
    # BUDGET PROGRESS
    # =====================================================

    side = tk.Frame(
        lower,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
        width=300
    )

    side.pack(
        side="left",
        fill="y"
    )

    side.pack_propagate(False)

    tk.Label(
        side,
        text="Budget Progress",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 12, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(17, 3)
    )

    tk.Label(
        side,
        text="Your spending this month",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8)
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 20)
    )

    spent = expenses

    percentage = (
        spent / budget * 100
        if budget
        else 0
    )

    percentage = min(max(percentage, 0), 100)

    # Amount spent
    tk.Label(
        side,
        text=f"RM {spent:,.2f}",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 21, "bold")
    ).pack(
        anchor="w",
        padx=20
    )

    tk.Label(
        side,
        text=f"of RM {budget:,.2f} monthly budget",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(
        anchor="w",
        padx=20,
        pady=(3, 16)
    )

    # Progress bar
    progress_frame = tk.Frame(
        side,
        bg="#E8F1F3",
        height=9
    )

    progress_frame.pack(
        fill="x",
        padx=20
    )

    progress_frame.pack_propagate(False)

    progress_fill = tk.Frame(
        progress_frame,
        bg=TEAL,
        height=9
    )

    progress_fill.place(
        relx=0,
        rely=0,
        relheight=1,
        relwidth=percentage / 100
    )

    # Percentage
    tk.Label(
        side,
        text=f"{percentage:.0f}% used",
        bg=WHITE,
        fg=TEAL,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="e",
        padx=20,
        pady=(8, 22)
    )

    # Divider
    tk.Frame(
        side,
        bg=BORDER,
        height=1
    ).pack(
        fill="x",
        padx=20,
        pady=(0, 18)
    )

    # Quick actions
    tk.Label(
        side,
        text="QUICK ACTIONS",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 10)
    )

    make_button(
        side,
        "Add Expense",
        show_budget_page,
        primary=True
    ).pack(
        fill="x",
        padx=20,
        pady=(0, 8)
    )

    make_button(
        side,
        "View Reports",
        show_reports_page
    ).pack(
        fill="x",
        padx=20
    )

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
        "Plan your budget, track income and manage your spending."
    )
    select_menu("Budget Management")

    # =====================================================
    # FINANCIAL SUMMARY
    # =====================================================

    budget, income, expenses, balance = get_financial_summary()

    summary_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    summary_frame.pack(
        fill="x",
        pady=(0, 18)
    )

    summary_data = [
        ("Monthly Budget", f"RM {budget:,.2f}", TEAL),
        ("Total Income", f"RM {income:,.2f}", BLUE),
        ("Total Expenses", f"RM {expenses:,.2f}", RED),
        ("Current Balance", f"RM {balance:,.2f}", YELLOW)
    ]

    for title, value, accent in summary_data:
        summary_card, _ = card(
            summary_frame,
            title,
            value,
            accent
        )

        summary_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

    # =====================================================
    # MAIN CONTENT
    # =====================================================

    forms = tk.Frame(
        content_frame,
        bg=BG
    )

    forms.pack(
        fill="both",
        expand=True
    )

    # =====================================================
    # BUDGET & INCOME CARD
    # =====================================================

    budget_box = tk.Frame(
        forms,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    budget_box.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 7)
    )

    # Header
    tk.Label(
        budget_box,
        text="Budget & Income",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 14, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(20, 3)
    )

    tk.Label(
        budget_box,
        text="Set your monthly budget and record money coming in.",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 20)
    )

    # Monthly budget
    tk.Label(
        budget_box,
        text="MONTHLY BUDGET",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 7)
    )

    budget_field, _ = field(
        budget_box,
        "Amount (RM)",
        budget_var
    )

    budget_field.pack(
        fill="x",
        padx=22
    )

    make_button(
        budget_box,
        "Save Budget",
        save_budget,
        primary=True
    ).pack(
        fill="x",
        padx=22,
        pady=(10, 20)
    )

    # Divider
    tk.Frame(
        budget_box,
        bg=BORDER,
        height=1
    ).pack(
        fill="x",
        padx=22,
        pady=(0, 20)
    )

    # Income
    tk.Label(
        budget_box,
        text="ADD INCOME",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 7)
    )

    income_field, _ = field(
        budget_box,
        "Income Amount (RM)",
        income_amount_var
    )

    income_field.pack(
        fill="x",
        padx=22,
        pady=(0, 12)
    )

    tk.Label(
        budget_box,
        text="Income Category",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 6)
    )

    income_menu = ttk.Combobox(
        budget_box,
        textvariable=income_category_var,
        values=[
            "Allowance",
            "Parents",
            "Part-Time Job",
            "Freelance Work",
            "Scholarship",
            "Gift",
            "Savings",
            "Other"
        ],
        state="readonly"
    )

    income_menu.pack(
        fill="x",
        padx=22
    )

    make_button(
        budget_box,
        "Add Income",
        add_income
    ).pack(
        fill="x",
        padx=22,
        pady=(12, 20)
    )

    # =====================================================
    # EXPENSE CARD
    # =====================================================

    expense_box = tk.Frame(
        forms,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    expense_box.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(7, 0)
    )

    # Header
    tk.Label(
        expense_box,
        text="Record Expense",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 14, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(20, 3)
    )

    tk.Label(
        expense_box,
        text="Record your spending to keep your balance updated.",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 20)
    )

    tk.Label(
        expense_box,
        text="EXPENSE DETAILS",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 7)
    )

    expense_field, _ = field(
        expense_box,
        "Expense Amount (RM)",
        expense_amount_var
    )

    expense_field.pack(
        fill="x",
        padx=22,
        pady=(0, 12)
    )

    tk.Label(
        expense_box,
        text="Expense Category",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        padx=22,
        pady=(0, 6)
    )

    expense_menu = ttk.Combobox(
        expense_box,
        textvariable=expense_category_var,
        values=[
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Education",
            "Health",
            "Other"
        ],
        state="readonly"
    )

    expense_menu.pack(
        fill="x",
        padx=22
    )

    date_field, _ = field(
        expense_box,
        "Date (YYYY-MM-DD)",
        transaction_date_var
    )

    date_field.pack(
        fill="x",
        padx=22,
        pady=12
    )

    make_button(
        expense_box,
        "Add Expense",
        add_expense,
        primary=True
    ).pack(
        fill="x",
        padx=22,
        pady=(0, 10)
    )

    # Current balance button
    make_button(
        expense_box,
        "Check Current Balance",
        lambda: messagebox.showinfo(
            "Current Balance",
            f"Income: RM {income:,.2f}\n"
            f"Expenses: RM {expenses:,.2f}\n"
            f"Balance: RM {balance:,.2f}"
        )
    ).pack(
        fill="x",
        padx=22,
        pady=(0, 20)
    )


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

    # =====================================================
    # FINANCIAL SUMMARY
    # =====================================================

    budget, income, expenses, balance = get_financial_summary()

    summary = tk.Frame(
        content_frame,
        bg=BG
    )

    summary.pack(
        fill="x",
        pady=(0, 16)
    )

    summary_data = [
        ("Total Income", f"RM {income:,.2f}", BLUE),
        ("Total Expenses", f"RM {expenses:,.2f}", RED),
        ("Current Balance", f"RM {balance:,.2f}", TEAL)
    ]

    for title, value, accent in summary_data:
        c, _ = card(
            summary,
            title,
            value,
            accent
        )

        c.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

    # =====================================================
    # TRANSACTION HISTORY CARD
    # =====================================================

    box = tk.Frame(
        content_frame,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    box.pack(
        fill="both",
        expand=True
    )

    # Header
    header = tk.Frame(
        box,
        bg=WHITE
    )

    header.pack(
        fill="x",
        padx=20,
        pady=(18, 12)
    )

    tk.Label(
        header,
        text="Transaction History",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 13, "bold")
    ).pack(
        side="left"
    )

    tk.Label(
        header,
        text="Your latest income and expenses",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 8)
    ).pack(
        side="left",
        padx=(12, 0)
    )

    # =====================================================
    # TABLE
    # =====================================================

    table_frame = tk.Frame(
        box,
        bg=WHITE
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20
    )

    columns = (
        "date",
        "category",
        "type",
        "amount"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    tree.heading(
        "date",
        text="DATE"
    )

    tree.heading(
        "category",
        text="CATEGORY"
    )

    tree.heading(
        "type",
        text="TYPE"
    )

    tree.heading(
        "amount",
        text="AMOUNT"
    )

    tree.column(
        "date",
        width=150,
        anchor="w"
    )

    tree.column(
        "category",
        width=220,
        anchor="w"
    )

    tree.column(
        "type",
        width=150,
        anchor="w"
    )

    tree.column(
        "amount",
        width=180,
        anchor="e"
    )

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

    # =====================================================
    # LOAD TRANSACTIONS
    # =====================================================

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

        amount_text = (
            f"+ RM {amount:,.2f}"
            if kind == "Income"
            else f"- RM {amount:,.2f}"
        )

        tree.insert(
            "",
            "end",
            iid=str(transaction_id),
            values=(
                dt,
                category,
                kind,
                amount_text
            ),
            tags=(kind,)
        )

    # =====================================================
    # TABLE STYLING
    # =====================================================

    tree.tag_configure(
        "Income",
        foreground=GREEN
    )

    tree.tag_configure(
        "Expense",
        foreground=RED
    )

    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not rows:

        tk.Label(
            table_frame,
            text="No transactions recorded yet.",
            bg=WHITE,
            fg=MUTED,
            font=("Arial", 9)
        ).pack(
            pady=25
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    actions = tk.Frame(
        box,
        bg=WHITE
    )

    actions.pack(
        fill="x",
        padx=20,
        pady=(12, 18)
    )

    def delete_selected():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select transaction",
                "Choose a transaction first."
            )
            return

        if not messagebox.askyesno(
            "Delete transaction",
            "Delete the selected transaction?"
        ):
            return

        connection = finance_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM Transactions
            WHERE transaction_id = ?
            AND user_id = ?
            """,
            (
                int(selected[0]),
                logged_in_user_id
            )
        )

        connection.commit()
        connection.close()

        show_transactions_page()

    make_button(
        actions,
        "Delete Selected",
        delete_selected
    ).pack(
        side="left"
    )

    make_button(
        actions,
        "Add New Transaction",
        show_budget_page,
        primary=True
    ).pack(
        side="right"
    )


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
        categories = [row[0] for row in category_rows]
        totals = [row[1] for row in category_rows]

        # Create pie chart
        figure = Figure(figsize=(5, 3.2), dpi=100)
        ax = figure.add_subplot(111)

        ax.pie(
            totals,
            labels=categories,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title(
            "Spending Distribution",
            fontsize=11,
            fontweight="bold"
        )

        # Keep the chart circular
        ax.axis("equal")

        # Embed Matplotlib chart into Tkinter
        canvas = FigureCanvasTkAgg(
            figure,
            master=left
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Display category totals below the chart
        for category, total in category_rows:
            row = tk.Frame(left, bg=WHITE)
            row.pack(fill="x", padx=18, pady=3)

            tk.Label(
                row,
                text=category,
                bg=WHITE,
                fg=TEXT,
                font=("Arial", 9, "bold")
            ).pack(side="left")

            tk.Label(
                row,
                text=f"RM {total:.2f}",
                bg=WHITE,
                fg=TEXT,
                font=("Arial", 9)
            ).pack(side="right")

    else:
            tk.Label(
            left,
            text="No expense data yet.",
            bg=WHITE,
            fg=MUTED,
            font=("Arial", 9)
        ).pack(
            anchor="w",
            padx=18,
            pady=18
        )
    

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

    clear_content()
    set_page_header(
        "Profile",
        "Manage your account information."
    )
    select_menu("Profile")

    layout = tk.Frame(content_frame, bg=BG)
    layout.pack(fill="both", expand=True)

    profile_card = tk.Frame(
        layout,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
        width=340
    )
    profile_card.pack(
        side="left",
        fill="y",
        padx=(0, 10)
    )
    profile_card.pack_propagate(False)

    # User information
    tk.Label(
        profile_card,
        text=get_username()[0].upper(),
        bg=NAVY_2,
        fg=WHITE,
        font=("Arial", 38, "bold"),
        width=4,
        height=2
    ).pack(pady=(60, 20))

    tk.Label(
        profile_card,
        text=get_username(),
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 16, "bold")
    ).pack()

    tk.Label(
        profile_card,
        text="Student Budget Tracker",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(pady=3)

    account = tk.Frame(
        layout,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    account.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0)
    )

    tk.Label(
        account,
        text="Account Information",
        bg=WHITE,
        fg=TEXT,
        font=("Arial", 13, "bold")
    ).pack(
        anchor="w",
        padx=24,
        pady=(22, 4)
    )

    tk.Label(
        account,
        text="Update your username or password below.",
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9)
    ).pack(
        anchor="w",
        padx=24,
        pady=(0, 18)
    )

    w, _ = field(
        account,
        "Username",
        profile_username_var
    )
    w.pack(
        fill="x",
        padx=24,
        pady=7
    )

    w, _ = field(
        account,
        "New Password",
        profile_password_var,
        show="*"
    )
    w.pack(
        fill="x",
        padx=24,
        pady=7
    )

    w, _ = field(
        account,
        "Confirm New Password",
        profile_confirm_var,
        show="*"
    )
    w.pack(
        fill="x",
        padx=24,
        pady=7
    )

    profile_username_var.set(get_username())
    profile_password_var.set("")
    profile_confirm_var.set("")


    def save_profile():
        global logged_in_user_id

        username = profile_username_var.get().strip()
        password = profile_password_var.get()
        confirm = profile_confirm_var.get()

        if not username:
            messagebox.showwarning(
                "Invalid username",
                "Username cannot be empty."
            )
            return

        if password != confirm:
            messagebox.showwarning(
                "Password mismatch",
                "The passwords do not match."
            )
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

            messagebox.showinfo(
                "Profile updated",
                "Your profile has been updated."
            )

            show_app()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Username unavailable",
                "That username is already in use."
            )

        finally:
            connection.close()

    make_button(
        account,
        "Save Changes",
        save_profile,
        primary=True
    ).pack(
        fill="x",
        padx=24,
        pady=(20, 7)
    )

    make_button(
        account,
        "Back to Dashboard",
        show_dashboard
    ).pack(
        fill="x",
        padx=24,
        pady=5
    )


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
