import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import pyodbc


class MonthSummaryForm:

    # ================= INIT =================
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_data()

    # ================= UI =================
    def build_ui(self):

        # -------- Title --------
        title_label = tk.Label(
            self.frame,
            text="मासिक आर्थिक अहवाल",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="blue"
        )
        title_label.pack(pady=15)

        # -------- Table Frame --------
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("महिना", "एकूण डेबिट", "एकूण क्रेडिट", "शिल्लक")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # -------- Exit Button --------
        exit_btn = tk.Button(
            self.frame,
            text="❌ बंद करा",
            bg="red",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=15,
            command=self.close_form
        )
        exit_btn.pack(pady=10)

    # ================= DATABASE CONNECTION =================
    def get_connection(self):
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= LOAD DATA =================
    def load_data(self):
        try:
            conn = self.get_connection()
            query = "SELECT Date1, Debit, Credit FROM dbo.Dailytrans1"
            df = pd.read_sql(query, conn)
            conn.close()

            if df.empty:
                messagebox.showinfo("माहिती", "कोणताही डेटा उपलब्ध नाही.")
                return

            # Convert Date
            df["Date1"] = pd.to_datetime(df["Date1"], errors="coerce")
            df = df.dropna(subset=["Date1"])

            if df.empty:
                messagebox.showinfo("माहिती", "कोणताही वैध तारीख डेटा उपलब्ध नाही.")
                return

            # Create Year-Month column
            df["वर्षमहिना"] = df["Date1"].dt.strftime("%Y-%m")

            # Group by Month
            summary = df.groupby("वर्षमहिना").agg(
                Debit=("Debit", "sum"),
                Credit=("Credit", "sum")
            ).reset_index()

            # Sort by month
            summary = summary.sort_values("वर्षमहिना")

            # Running Balance
            running_balance = 0
            balances = []

            for _, row in summary.iterrows():
                monthly_balance = row["Credit"] - row["Debit"]
                running_balance += monthly_balance
                balances.append(running_balance)

            summary["शिल्लक"] = balances

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            # Insert data
            for _, row in summary.iterrows():
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["वर्षमहिना"],
                        f"{float(row['Debit']):,.2f}",
                        f"{float(row['Credit']):,.2f}",
                        f"{float(row['शिल्लक']):,.2f}"
                    )
                )

        except Exception as e:
            messagebox.showerror("त्रुटी", f"डेटा लोड करताना समस्या:\n{str(e)}")

    # ================= CLOSE FORM =================
    def close_form(self):
        if messagebox.askyesno("बंद करा", "आपण हा अहवाल बंद करू इच्छिता का?"):
            self.frame.destroy()