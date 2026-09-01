import tkinter as tk
from tkinter import messagebox
import sqlite3

# Stores the ID of the currently logged-in user
logged_in_user_id = None


# Create and connect to the database
def create_database():
    connection = sqlite3.connect("budget_tracker.db")
    cursor = connection.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Create database when the program starts
create_database()
# Register a new user
def register_user():
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_entry.get()

    # Check for empty fields 
    if username =="" or password =="" or confirm_password =="":
        messagebox.showerror("Error","Please fill in all fields.")
        return

    # Check whether passwords match
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return
    try:
        connection = sqlite3.connect("budget_tracker.db")
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password)
        )

        connection.commit()
        connection.close()

        messagebox.showinfo("Success", "Registration successful.")

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

# Create the main application window
root = tk.Tk()
root.title("Student Budget Tracker - Registration")
root.geometry("400x350")
root.resizable(False, False)


# Show login screen
def logout_user():
    global logged_in_user_id

    # Clear the current user's session
    logged_in_user_id = None

    messagebox.showinfo("Logout", "You have been logged out.")

    show_login()

def show_dashboard():
    # Remove everything from the current screen
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Student Budget Tracker")

    welcome_label = tk.Label(
        root,
        text="Welcome Back! 👋",
        font=("Arial", 18, "bold")
    )
    welcome_label.pack(pady=(50, 5))

    subtitle_label = tk.Label(
        root,
        text="Ready to manage your money?",
        font=("Arial", 11)
    )
    subtitle_label.pack(pady=5)

    logout_button = tk.Button(
        root,
        text="Logout",
        width=20,
        command=logout_user
    )
    logout_button.pack(pady=20)

def login_user(username_entry, password_entry):
    global logged_in_user_id

    username = username_entry.get()
    password = password_entry.get()

    # Check for empty fields
    if username == "" or password == "":
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    connection = sqlite3.connect("budget_tracker.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    user = cursor.fetchone()
    connection.close()

    if user:
        logged_in_user_id = user[0]

        messagebox.showinfo(
            "Success", 
            "Login successful!"
         )
        show_dashboard()
    else:
        messagebox.showerror(
            "Error", "Incorrect username or password."
            )

def show_login():
    # Remove the registration widgets
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Student Budget Tracker - Login")

    # Login title
    login_title = tk.Label(
        root,
        text="Login",
        font=("Arial", 20, "bold")
    )
    login_title.pack(pady=25)

    # Username
    login_username_label = tk.Label(root, text="Username")
    login_username_label.pack()

    login_username_entry = tk.Entry(root, width=30)
    login_username_entry.pack(pady=5)

    # Password
    login_password_label = tk.Label(root, text="Password")
    login_password_label.pack()

    login_password_entry = tk.Entry(root, width=30, show="*")
    login_password_entry.pack(pady=5)

    # Login button
    login_button = tk.Button(
    root,
    text="Login",
    width=20,
    command=lambda: login_user(
        login_username_entry,
        login_password_entry
    )
)
    login_button.pack(pady=20)

    register_page_button = tk.Button(
    root,
    text="Don't have an account? Create Account",
    command=show_register
)
    register_page_button = tk.Button(
        root,
        text="Don't have an account? Create Account",
        command=show_register
    )
    register_page_button.pack()

    # Allow Enter key to login
    root.bind(
        "<Return>",
        lambda event: login_user(
            login_username_entry,
            login_password_entry
        )
    )

# Registration title
# Show registration screen
def show_register():
    global username_entry, password_entry, confirm_entry

    # Remove everything from the current screen
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Student Budget Tracker - Registration")

    # Registration title
    title_label = tk.Label(
        root,
        text="Create Account",
        font=("Arial", 20, "bold")
    )
    title_label.pack(pady=25)

    # Username
    username_label = tk.Label(root, text="Username")
    username_label.pack()

    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    # Password
    password_label = tk.Label(root, text="Password")
    password_label.pack()

    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    # Confirm password
    confirm_label = tk.Label(root, text="Confirm Password")
    confirm_label.pack()

    confirm_entry = tk.Entry(root, width=30, show="*")
    confirm_entry.pack(pady=5)

    # Register button
    register_button = tk.Button(
        root,
        text="Register",
        width=20,
        command=register_user
    )
    register_button.pack(pady=20)

    # Go to login screen
    login_page_button = tk.Button(
        root,
        text="Already have an account? Login",
        command=show_login
    )
    login_page_button.pack()

    # Allow Enter key to register
    root.bind("<Return>", lambda event: register_user())

show_register()

root.mainloop()
 