import sqlite3

try:
    connection = sqlite3.connect("budget_tracker.db")
    print("Database connection succesfull.")

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
    )
    """)

    connection.commit()

    print("Users table created succesfully.")

    connection.close()
    print("Database connection closed.")

except sqlite3.Error as error:
    print("Error connecting to database:", error)