import tkinter as tk
from tkinter import messagebox
import pyodbc


# ================= DATABASE =================
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=Sarthak;"
        "DATABASE=Socity_db;"
        "Trusted_Connection=yes;"
    )


# ================= CENTER WINDOW FUNCTION =================
def center_window(window, width=400, height=300):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x}+{y}")


# ================= LOGIN FORM =================
class LoginForm:

    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        # Center the window
        center_window(self.root, 400, 300)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):

        tk.Label(self.root,
                 text="LOGIN SYSTEM",
                 font=("Segoe UI", 18, "bold"),
                 bg="#2c3e50",
                 fg="white",
                 pady=10).pack(fill="x")

        frame = tk.Frame(self.root)
        frame.pack(pady=40)

        tk.Label(frame, text="Username").grid(row=0, column=0, pady=10)
        tk.Entry(frame, textvariable=self.username).grid(row=0, column=1)

        tk.Label(frame, text="Password").grid(row=1, column=0, pady=10)
        tk.Entry(frame, textvariable=self.password, show="*").grid(row=1, column=1)

        tk.Button(self.root,
                  text="Login",
                  width=15,
                  command=self.login).pack(pady=10)

    # ================= LOGIN FUNCTION =================
    def login(self):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM Users
            WHERE Username=? AND Password=?
        """, (self.username.get(), self.password.get()))

        result = cur.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Success", "Login Successful")
            self.open_main_menu()
        else:
            messagebox.showerror("Error", "Invalid Login")

    # ================= OPEN MAIN MENU =================
    def open_main_menu(self):
        self.root.destroy()

        from main_menu import MainMenu

        new_root = tk.Tk()
        center_window(new_root, 800, 600)  # center main menu also
        app = MainMenu(new_root)
        new_root.mainloop()


# ================= START FUNCTION =================
def start_login():
    root = tk.Tk()
    app = LoginForm(root)
    root.mainloop()


if __name__ == "__main__":
    start_login()