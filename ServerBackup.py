import tkinter as tk
from tkinter import filedialog, messagebox
import pyodbc

class SQLBackupApp:

    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):

        tk.Label(self.frame, text="Server:").grid(row=0, column=0)
        self.entry_server = tk.Entry(self.frame)
        self.entry_server.grid(row=0, column=1)

        tk.Label(self.frame, text="Database:").grid(row=1, column=0)
        self.entry_database = tk.Entry(self.frame)
        self.entry_database.grid(row=1, column=1)

        tk.Label(self.frame, text="Username:").grid(row=2, column=0)
        self.entry_username = tk.Entry(self.frame)
        self.entry_username.grid(row=2, column=1)

        tk.Label(self.frame, text="Password:").grid(row=3, column=0)
        self.entry_password = tk.Entry(self.frame, show="*")
        self.entry_password.grid(row=3, column=1)

        tk.Button(
            self.frame,
            text="Backup Database",
            command=self.backup_database
        ).grid(row=4, columnspan=2, pady=10)

    def backup_database(self):

        server = self.entry_server.get()
        database = self.entry_database.get()
        username = self.entry_username.get()
        password = self.entry_password.get()

        file_path = filedialog.asksaveasfilename(
            defaultextension=".bak",
            filetypes=[("Backup Files", "*.bak")]
        )

        if not file_path:
            return

        try:
            conn = pyodbc.connect(
                f"DRIVER={{SQL Server}};"
                f"SERVER={server};"
                f"DATABASE=master;"
                f"UID={username};"
                f"PWD={password}",
                autocommit=True
            )

            cursor = conn.cursor()

            query = f"""
            BACKUP DATABASE [{database}]
            TO DISK = '{file_path}'
            WITH FORMAT, INIT
            """

            cursor.execute(query)

            messagebox.showinfo("Success", "Backup completed!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            try:
                conn.close()
            except:
                pass