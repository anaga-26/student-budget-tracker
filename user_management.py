import tkinter as tk
from tkinter import messagebox
import sqlite3


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
        messagebox.showerror("error","Please fill in all fields.")
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

        messagebox.showinfo("Success","Registration successfull")

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)

    except sqlite3.IntegrityError:
        messagebox.showerror("Error","Username already exists.")

# Create registration window
root = tk.Tk()
root.title("Student Budget Tracker - Registration")
root.geometry("400x350")
root.resizable(False, False)


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
register_button.pack(pady=25)


root.mainloop()
 