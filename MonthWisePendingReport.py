import tkinter as tk
from tkinter import ttk
import pyodbc
import pandas as pd


class MonthWisePendingReport:

    def __init__(self, parent):

        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

        self.root = parent
        self.root.title("Month Wise Pending Report")
        self.root.geometry("850x520")

        self.create_ui()
        self.load_years()

    # ---------------- UI ----------------

    def create_ui(self):

        tk.Label(
            self.root,
            text="Month Wise Pending Maintenance Report",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Month
        tk.Label(filter_frame, text="Month").grid(row=0, column=0, padx=10)

        self.month_combo = ttk.Combobox(
            filter_frame,
            state="readonly",
            width=12,
            values=[
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December"
            ]
        )
        self.month_combo.grid(row=0, column=1)

        # Year
        tk.Label(filter_frame, text="Year").grid(row=0, column=2, padx=10)

        self.year_combo = ttk.Combobox(
            filter_frame,
            state="readonly",
            width=10
        )
        self.year_combo.grid(row=0, column=3)

        tk.Button(
            filter_frame,
            text="Search",
            command=self.load_report,
            bg="#4CAF50",
            fg="white",
            width=12
        ).grid(row=0, column=4, padx=10)

        # Total Label
        self.total_label = tk.Label(
            self.root,
            text="Total Pending : 0",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        self.total_label.pack(pady=5)

        # Treeview
        cols = ("Flat_No", "Member_Name", "Monthly_Maintenance", "Paid", "Pending")

        self.tree = ttk.Treeview(
            self.root,
            columns=cols,
            show="headings",
            height=15
        )

        self.tree.heading("Flat_No", text="Flat No")
        self.tree.heading("Member_Name", text="Member Name")
        self.tree.heading("Monthly_Maintenance", text="Maintenance")
        self.tree.heading("Paid", text="Paid Amount")
        self.tree.heading("Pending", text="Pending Amount")

        self.tree.column("Flat_No", width=100, anchor="center")
        self.tree.column("Member_Name", width=250, anchor="w")
        self.tree.column("Monthly_Maintenance", width=120, anchor="e")
        self.tree.column("Paid", width=120, anchor="e")
        self.tree.column("Pending", width=120, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.tag_configure("pending", background="#ffcccc")

    # ---------------- LOAD YEARS ----------------

    def load_years(self):

        query = "SELECT DISTINCT Year FROM Yearly_Flat_Maintenance ORDER BY Year"

        df = pd.read_sql_query(query, self.conn)

        self.year_combo["values"] = list(df["Year"])

    # ---------------- CLEAR TREE ----------------

    def clear_tree(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

    # ---------------- LOAD REPORT ----------------

    def load_report(self):

        month_name = self.month_combo.get()
        year = self.year_combo.get()

        if not month_name or not year:
            return

        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        month = month_map[month_name]

        query = f"""
        SELECT
            m.Flat_No,
            m.Member_Name,
            y.Monthly_Amount,
            ISNULL(SUM(d.Credit),0) AS Paid,
            (y.Monthly_Amount * {month}) - ISNULL(SUM(d.Credit),0) AS Pending
        FROM Member_Mast m
        INNER JOIN Yearly_Flat_Maintenance y
            ON m.Flat_No = y.Flat_No
            AND y.Year = {year}
        LEFT JOIN Dailytrans1 d
            ON m.Flat_No = d.Flat_No
            AND MONTH(d.Date1) <= {month}
            AND YEAR(d.Date1) = {year}
        GROUP BY
            m.Flat_No,
            m.Member_Name,
            y.Monthly_Amount
        ORDER BY m.Flat_No
        """

        df = pd.read_sql_query(query, self.conn)

        self.clear_tree()

        total_pending = 0

        for _, r in df.iterrows():

            pending = float(r["Pending"])

            if pending < 0:
                pending = 0

            total_pending += pending

            tag = ""
            if pending > 0:
                tag = "pending"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    r["Flat_No"],
                    r["Member_Name"],
                    f"{r['Monthly_Amount']:,.2f}",
                    f"{r['Paid']:,.2f}",
                    f"{pending:,.2f}"
                ),
                tags=(tag,)
            )

        self.total_label.config(text=f"Total Pending : {total_pending:,.2f}")


# ---------------- MAIN PROGRAM ----------------

if __name__ == "__main__":

    root = tk.Tk()

    app = MonthWisePendingReport(root)

    root.mainloop()