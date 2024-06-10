import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib

# Initialize database connection
conn = sqlite3.connect('banking_system.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY,
             username TEXT UNIQUE,
             password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions (
             id INTEGER PRIMARY KEY,
             user_id INTEGER,
             type TEXT,
             amount REAL,
             balance REAL,
             date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY(user_id) REFERENCES users(id))''')

conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    try:
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        messagebox.showinfo("Success", "Registration Successful")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")

def login(username, password):
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = c.fetchone()
    if user:
        return user[0]  # Return user_id
    else:
        messagebox.showerror("Error", "Invalid credentials")
        return None

def get_balance(user_id):
    c.execute("SELECT balance FROM transactions WHERE user_id=? ORDER BY date DESC LIMIT 1", (user_id,))
    balance = c.fetchone()
    return balance[0] if balance else 0.0

def create_account(user_id):
    initial_balance = 0.0
    c.execute("INSERT INTO transactions (user_id, type, amount, balance) VALUES (?, ?, ?, ?)",
              (user_id, 'CREATE', initial_balance, initial_balance))
    conn.commit()

def deposit(user_id, amount):
    balance = get_balance(user_id)
    new_balance = balance + amount
    c.execute("INSERT INTO transactions (user_id, type, amount, balance) VALUES (?, ?, ?, ?)",
              (user_id, 'DEPOSIT', amount, new_balance))
    conn.commit()
    messagebox.showinfo("Success", f"Deposited {amount}. New balance: {new_balance}")

def withdraw(user_id, amount):
    balance = get_balance(user_id)
    if amount > balance:
        messagebox.showerror("Error", "Insufficient funds")
    else:
        new_balance = balance - amount
        c.execute("INSERT INTO transactions (user_id, type, amount, balance) VALUES (?, ?, ?, ?)",
                  (user_id, 'WITHDRAW', amount, new_balance))
        conn.commit()
        messagebox.showinfo("Success", f"Withdrew {amount}. New balance: {new_balance}")

def get_transaction_history(user_id):
    c.execute("SELECT type, amount, balance, date FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
    return c.fetchall()

class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Banking System")
        self.user_id = None

        # Center the window
        window_width = 400
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Login/Register frame
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True)

        self.username_label = tk.Label(self.frame, text="Username")
        self.username_label.grid(row=0, column=0, pady=10)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, pady=10)

        self.password_label = tk.Label(self.frame, text="Password")
        self.password_label.grid(row=1, column=0, pady=10)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)

        self.login_button = tk.Button(self.frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, pady=10)

        self.register_button = tk.Button(self.frame, text="Register", command=self.register)
        self.register_button.grid(row=2, column=1, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.user_id = login(username, password)
        if self.user_id:
            self.load_account_management()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        register(username, password)

    def load_account_management(self):
        self.frame.pack_forget()
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True)

        self.balance_button = tk.Button(self.frame, text="Check Balance", command=self.check_balance)
        self.balance_button.grid(row=0, column=0, pady=10)

        self.deposit_label = tk.Label(self.frame, text="Deposit Amount")
        self.deposit_label.grid(row=1, column=0, pady=10)
        self.deposit_entry = tk.Entry(self.frame)
        self.deposit_entry.grid(row=1, column=1, pady=10)
        self.deposit_button = tk.Button(self.frame, text="Deposit", command=self.deposit)
        self.deposit_button.grid(row=1, column=2, pady=10)

        self.withdraw_label = tk.Label(self.frame, text="Withdraw Amount")
        self.withdraw_label.grid(row=2, column=0, pady=10)
        self.withdraw_entry = tk.Entry(self.frame)
        self.withdraw_entry.grid(row=2, column=1, pady=10)
        self.withdraw_button = tk.Button(self.frame, text="Withdraw", command=self.withdraw)
        self.withdraw_button.grid(row=2, column=2, pady=10)

        self.history_button = tk.Button(self.frame, text="Transaction History", command=self.transaction_history)
        self.history_button.grid(row=3, column=0, pady=10)

    def check_balance(self):
        balance = get_balance(self.user_id)
        messagebox.showinfo("Balance", f"Current balance: {balance}")

    def deposit(self):
        try:
            amount = float(self.deposit_entry.get())
            deposit(self.user_id, amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for deposit amount")

    def withdraw(self):
        try:
            amount = float(self.withdraw_entry.get())
            withdraw(self.user_id, amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for withdraw amount")

    def transaction_history(self):
        history = get_transaction_history(self.user_id)
        history_str = "\n".join([f"{type_}: {amount} - Balance: {balance} on {date}" for type_, amount, balance, date in history])
        messagebox.showinfo("Transaction History", history_str)

if __name__ == "__main__":
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()
    conn.close()
