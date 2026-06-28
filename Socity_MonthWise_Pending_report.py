import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyodbc
import pandas as pd
import tempfile
import webbrowser

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class MonthPendingReport:

    def __init__(self, parent):

        self.win = tk.Toplevel(parent)
        self.win.title("Maintenance vs Payment Report")
        self.win.geometry("1350x600")

        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

        self.df = pd.DataFrame()

        self.create_widgets()

    # ----------------------------
    # UI
    # ----------------------------
    def create_widgets(self):

        heading = tk.Label(
        self.win,
        text="Member Pending Report",
        font=("Arial", 16, "bold"),
        fg="#2c3e50"
        )
        heading.pack(pady=5)

        top = tk.Frame(self.win)
        top.pack(pady=10)

        tk.Label(top, text="Year").grid(row=0, column=0)

        self.year_var = tk.IntVar(value=2026)

        ttk.Combobox(
            top,
            textvariable=self.year_var,
            values=(2024, 2025, 2026, 2027),
            width=10
        ).grid(row=0, column=1, padx=5)

        tk.Label(top, text="Flat Search").grid(row=0, column=2)

        self.search_var = tk.StringVar()

        tk.Entry(top, textvariable=self.search_var, width=15).grid(row=0, column=3)

        tk.Button(top, text="Search", command=self.search_flat).grid(row=0, column=4, padx=5)

        tk.Button(
            top,
            text="Load Report",
            command=self.load_report,
            bg="#3498db",
            fg="white"
        ).grid(row=0, column=5, padx=10)

        # TABLE
        columns = [
            "Flat", "Member",
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "TotalMaintenance", "TotalPayment", "Pending"
        ]

        self.tree = ttk.Treeview(self.win, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=85)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # DOUBLE CLICK LEDGER
        self.tree.bind("<Double-1>", self.open_ledger)

        # BOTTOM BUTTONS
        bottom = tk.Frame(self.win)
        bottom.pack(pady=10)

        tk.Button(bottom, text="Export Excel",
                  command=self.export_excel).grid(row=0, column=0, padx=10)

        tk.Button(bottom, text="Print Report",
                  command=self.print_report).grid(row=0, column=1, padx=10)

        tk.Button(bottom, text="Export PDF",
                  command=self.export_pdf).grid(row=0, column=2, padx=10)

    # ----------------------------
    # LOAD REPORT
    # ----------------------------
    def load_report(self):

        year = self.year_var.get()

        query = f"""
        SELECT 
        m.Flat_No,
        m.Member_Name,
        ISNULL(y.Monthly_Amount,0) AS MonthlyMaintenance,

        SUM(CASE WHEN MONTH(d.Date1)=1 THEN d.Credit ELSE 0 END) AS Jan,
        SUM(CASE WHEN MONTH(d.Date1)=2 THEN d.Credit ELSE 0 END) AS Feb,
        SUM(CASE WHEN MONTH(d.Date1)=3 THEN d.Credit ELSE 0 END) AS Mar,
        SUM(CASE WHEN MONTH(d.Date1)=4 THEN d.Credit ELSE 0 END) AS Apr,
        SUM(CASE WHEN MONTH(d.Date1)=5 THEN d.Credit ELSE 0 END) AS May,
        SUM(CASE WHEN MONTH(d.Date1)=6 THEN d.Credit ELSE 0 END) AS Jun,
        SUM(CASE WHEN MONTH(d.Date1)=7 THEN d.Credit ELSE 0 END) AS Jul,
        SUM(CASE WHEN MONTH(d.Date1)=8 THEN d.Credit ELSE 0 END) AS Aug,
        SUM(CASE WHEN MONTH(d.Date1)=9 THEN d.Credit ELSE 0 END) AS Sep,
        SUM(CASE WHEN MONTH(d.Date1)=10 THEN d.Credit ELSE 0 END) AS Oct,
        SUM(CASE WHEN MONTH(d.Date1)=11 THEN d.Credit ELSE 0 END) AS Nov,
        SUM(CASE WHEN MONTH(d.Date1)=12 THEN d.Credit ELSE 0 END) AS Dec,

        SUM(ISNULL(d.Credit,0)) AS TotalPayment

        FROM Member_Mast m

        LEFT JOIN Dailytrans1 d
        ON m.Flat_No = d.Flat_No
        AND YEAR(d.Date1) = {year}

        LEFT JOIN Yearly_Flat_Maintenance y
        ON m.Flat_No = y.Flat_No
        AND y.Year = {year}

        GROUP BY
        m.Flat_No,
        m.Member_Name,
        y.Monthly_Amount

        ORDER BY m.Flat_No
        """

        df = pd.read_sql(query, self.conn)

        df.rename(columns={
            "Flat_No": "Flat",
            "Member_Name": "Member"
        }, inplace=True)

        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]

        monthly_amt = df["MonthlyMaintenance"]

        for m in months:
            df[m] = monthly_amt - df[m]

        df["TotalMaintenance"] = monthly_amt * 12
        df["Pending"] = df["TotalMaintenance"] - df["TotalPayment"]

        df.drop(columns=["MonthlyMaintenance"], inplace=True)

        self.df = df

        self.show_table(df)

    # ----------------------------
    # SHOW TABLE
    # ----------------------------
    def show_table(self, data):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, r in data.iterrows():
            self.tree.insert("", tk.END, values=list(r))

    # ----------------------------
    # SEARCH
    # ----------------------------
    def search_flat(self):

        text = self.search_var.get()

        if text == "":
            self.show_table(self.df)
            return

        data = self.df[self.df["Flat"].astype(str).str.contains(text)]

        self.show_table(data)

    # ----------------------------
    # LEDGER POPUP
    # ----------------------------
    def open_ledger(self, event):

        selected = self.tree.focus()
        values = self.tree.item(selected, "values")

        if not values:
            return

        flat = values[0]

        win = tk.Toplevel(self.win)
        win.title(f"Flat Ledger - {flat}")
        win.geometry("700x400")

        tree = ttk.Treeview(win, columns=("Date", "Debit", "Credit"), show="headings")

        tree.heading("Date", text="Date")
        tree.heading("Debit", text="Debit")
        tree.heading("Credit", text="Credit")

        tree.pack(fill="both", expand=True)

        query = f"""
        SELECT Date1, Debit, Credit
        FROM Dailytrans1
        WHERE Flat_No={flat}
        ORDER BY Date1
        """

        df = pd.read_sql(query, self.conn)

        for _, r in df.iterrows():
            tree.insert("", tk.END, values=list(r))

    # ----------------------------
    # EXPORT EXCEL
    # ----------------------------
    def export_excel(self):

        file = filedialog.asksaveasfilename(defaultextension=".xlsx")

        if file:
            self.df.to_excel(file, index=False)
            messagebox.showinfo("Export", "Excel Exported")

    # ----------------------------
    # EXPORT PDF
    # ----------------------------
    def export_pdf(self):

        file = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

        if not file:
            return

        year = self.year_var.get()

    # REGISTER MARATHI FONT
        pdfmetrics.registerFont(TTFont('Mangal', 'Mangal.ttf'))

        doc = SimpleDocTemplate(file, pagesize=landscape(A4))

        elements = []

        styles = getSampleStyleSheet()

        title = Paragraph(
        f"<font name='Mangal'><b>Member Pending Report - {year}</b></font>",
        styles['Title']
        )

        elements.append(title)
        elements.append(Spacer(1, 20))

        data = [list(self.df.columns)]

        for _, row in self.df.iterrows():
            data.append([str(x) for x in row])

        table = Table(data, repeatRows=1)

        table.setStyle(TableStyle([

        ("FONTNAME", (0,0), (-1,-1), "Mangal"),

        ("BACKGROUND",(0,0),(-1,0),colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("GRID",(0,0),(-1,-1),1,colors.black)

        ]))

        elements.append(table)

        doc.build(elements)

        messagebox.showinfo("PDF Export", "PDF Report Created Successfully")

    # ----------------------------
    # PRINT REPORT
    # ----------------------------
    def print_report(self):

        html = "<h2>Maintenance vs Payment Report</h2>"
        html += self.df.to_html(index=False)

        file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")

        with open(file.name, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(file.name)


# ----------------------------
# MAIN PROGRAM
# ----------------------------
if __name__ == "__main__":

    root = tk.Tk()
    root.title("Society Management System")
    root.geometry("300x200")

    tk.Button(
        root,
        text="Member Maintenance Pending Report",
        command=lambda: MonthPendingReport(root),
        font=("Arial", 12),
        width=22,
        bg="#2ecc71",
        fg="white"
    ).pack(pady=60)

    root.mainloop()