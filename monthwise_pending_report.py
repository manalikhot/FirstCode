import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyodbc
import pandas as pd
import webbrowser
import urllib.parse
import os


class MonthwisePendingReport:

    def __init__(self, parent):

        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title("Society Maintenance Report")
        self.win.geometry("960x520")

        # DB CONNECTION
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

        self.df = pd.DataFrame()

        self.create_widgets()

    # -------------------------------------
    # UI LAYOUT
    # -------------------------------------
    def create_widgets(self):

        top = tk.Frame(self.win)
        top.pack(pady=10)

        tk.Label(top, text="Year").grid(row=0, column=0)

        self.year_var = tk.IntVar(value=2026)

        year_box = ttk.Combobox(top, textvariable=self.year_var, width=10)
        year_box["values"] = (2024, 2025, 2026, 2027)
        year_box.grid(row=0, column=1)

        tk.Label(top, text="Month").grid(row=0, column=2)

        self.month_var = tk.IntVar(value=12)

        month_box = ttk.Combobox(top, textvariable=self.month_var, width=10)
        month_box["values"] = tuple(range(1, 13))
        month_box.grid(row=0, column=3)

        tk.Button(top, text="Load Report",
                  command=self.load_report,
                  bg="#3498db", fg="white").grid(row=0, column=4, padx=10)

        tk.Button(top, text="Pending Only",
                  command=self.show_pending,
                  bg="#f39c12", fg="white").grid(row=0, column=5)

        tk.Button(top, text="Advance Only",
                  command=self.show_advance,
                  bg="#2ecc71", fg="white").grid(row=0, column=6)

        # TABLE
        self.tree = ttk.Treeview(self.win)

        self.tree["columns"] = (
            "Flat_No",
            "Member_Name",
            "OpeningBalance",
            "Maintenance",
            "Payment",
            "PendingBalance"
        )

        self.tree["show"] = "headings"

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.tag_configure(
            "total",
            background="#dff0d8",
            font=("Arial", 10, "bold")
        )

        # BOTTOM BUTTONS
        bottom = tk.Frame(self.win)
        bottom.pack(pady=10)

        tk.Button(bottom,
                  text="WhatsApp Reminder",
                  command=self.send_whatsapp,
                  bg="#25D366",
                  fg="white",
                  font=("Arial", 10, "bold")
                  ).grid(row=0, column=0, padx=10)

        tk.Button(bottom,
                  text="Export Excel",
                  command=self.export_excel
                  ).grid(row=0, column=1, padx=10)

        tk.Button(bottom,
                  text="Print Report",
                  command=self.print_report
                  ).grid(row=0, column=2, padx=10)

        tk.Button(bottom,
                  text="Exit",
                  command=self.win.destroy,
                  bg="red",
                  fg="white"
                  ).grid(row=0, column=3, padx=10)

    # -------------------------------------
    # LOAD REPORT
    # -------------------------------------
    def load_report(self):

        year = self.year_var.get()
        month = self.month_var.get()

        query = f"""
        SELECT 
        m.Flat_No,
        m.Member_Name,
        m.Member_Mob1,

        CAST(ISNULL(o.Debit,0)-ISNULL(o.Credit,0) AS DECIMAL(18,2)) AS OpeningBalance,

        CAST(ISNULL(y.Monthly_Amount,0) * {month} AS DECIMAL(18,2)) AS Maintenance,

        CAST(ISNULL(SUM(d.Credit),0) AS DECIMAL(18,2)) AS Payment,

        CAST(
        (
        (ISNULL(o.Debit,0)-ISNULL(o.Credit,0))
        +
        (ISNULL(y.Monthly_Amount,0) * {month})
        -
        ISNULL(SUM(d.Credit),0)
        )
        AS DECIMAL(18,2)) AS PendingBalance

        FROM Member_Mast m

        LEFT JOIN Opening_Balance o
        ON m.Flat_No = o.Flat_No AND o.Year = {year}

        LEFT JOIN Yearly_Flat_Maintenance y
        ON m.Flat_No = y.Flat_No AND y.Year = {year}

        LEFT JOIN Dailytrans1 d
        ON m.Flat_No = d.Flat_No
        AND YEAR(d.Date1) = {year}
        AND MONTH(d.Date1) <= {month}

        GROUP BY
        m.Flat_No,
        m.Member_Name,
        m.Member_Mob1,
        o.Debit,
        o.Credit,
        y.Monthly_Amount

        ORDER BY m.Flat_No
        """

        self.df = pd.read_sql(query, self.conn)

        self.show_table(self.df)

    # -------------------------------------
    # SHOW TABLE
    # -------------------------------------
    def show_table(self, data):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in data.iterrows():

            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["Flat_No"],
                    row["Member_Name"],
                    f"{row['OpeningBalance']:.2f}",
                    f"{row['Maintenance']:.2f}",
                    f"{row['Payment']:.2f}",
                    f"{row['PendingBalance']:.2f}"
                )
            )

        open_total = data["OpeningBalance"].sum()
        main_total = data["Maintenance"].sum()
        pay_total = data["Payment"].sum()
        pend_total = data["PendingBalance"].sum()

        self.tree.insert(
            "",
            tk.END,
            values=("TOTAL", "",
                    f"{open_total:.2f}",
                    f"{main_total:.2f}",
                    f"{pay_total:.2f}",
                    f"{pend_total:.2f}"
                    ),
            tags=("total",)
        )

    # -------------------------------------
    # FILTERS
    # -------------------------------------
    def show_pending(self):

        data = self.df[self.df["PendingBalance"] > 0]
        self.show_table(data)

    def show_advance(self):

        data = self.df[self.df["PendingBalance"] < 0]
        self.show_table(data)

    # -------------------------------------
    # WHATSAPP
    # -------------------------------------
    def send_whatsapp(self):

        selected = self.tree.focus()

        if not selected:
            messagebox.showwarning("Select Member", "Please select member")
            return

        values = self.tree.item(selected, "values")
        flat = values[0]

        member = self.df[self.df["Flat_No"] == int(flat)].iloc[0]

        mobile = member["Member_Mob1"]
        pending = member["PendingBalance"]

        message = f"""
Dear {member['Member_Name']},

Your society maintenance pending amount is ₹{pending:.2f}.

Kindly pay at the earliest.

Thank you
Society Office
"""

        encoded = urllib.parse.quote(message)

        url = f"https://wa.me/91{mobile}?text={encoded}"

        webbrowser.open(url)

    # -------------------------------------
    # EXPORT
    # -------------------------------------
    def export_excel(self):

        file = filedialog.asksaveasfilename(defaultextension=".xlsx")

        if file:
            self.df.to_excel(file, index=False)

    # -------------------------------------
    # PRINT
    # -------------------------------------
    def print_report(self):

        temp_file = "report.xlsx"

        self.df.to_excel(temp_file, index=False)

        os.startfile(temp_file, "print")