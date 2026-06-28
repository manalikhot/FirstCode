import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pyodbc
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors


class MonthWiseDashboard(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Accounting Dashboard")
        self.center_window(1100, 750)

        self.df_report = None

        self.create_widgets()
        self.load_accounts()

    # ================= CENTER WINDOW =================
    def center_window(self, width, height):

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))

        self.geometry(f"{width}x{height}+{x}+{y}")

    # ================= DATABASE =================
    def get_connection(self):

        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= UI =================
    def create_widgets(self):

        # -------- Filter Frame --------
        filter_frame = ttk.LabelFrame(self, text="Filters")
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="From").grid(row=0, column=0)
        self.cal_from = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        self.cal_from.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="To").grid(row=0, column=2)
        self.cal_to = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        self.cal_to.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Account").grid(row=0, column=4)

        self.account_combo = ttk.Combobox(filter_frame, width=25)
        self.account_combo.grid(row=0, column=5)

        ttk.Button(filter_frame, text="Load",
                   command=self.load_report).grid(row=0, column=6, padx=5)

        ttk.Button(filter_frame, text="Excel",
                   command=self.export_excel).grid(row=0, column=7, padx=5)

        ttk.Button(filter_frame, text="PDF",
                   command=self.export_pdf).grid(row=0, column=8, padx=5)

        ttk.Button(filter_frame, text="Exit",
                   command=self.destroy).grid(row=0, column=9, padx=5)

        # -------- Summary Cards --------
        card_frame = tk.Frame(self)
        card_frame.pack(fill="x", pady=10)

        self.card_debit = self.create_card(card_frame, "Total Debit", "#e74c3c")
        self.card_credit = self.create_card(card_frame, "Total Credit", "#27ae60")
        self.card_profit = self.create_card(card_frame, "Net Profit", "#2980b9")

        # -------- Table --------
        columns = ("Month-Year", "Debit", "Credit", "Net")

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=200)

        self.tree.pack(fill="x", padx=10)

        # -------- Chart --------
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True)

    # ================= CARD UI =================
    def create_card(self, parent, title, color):

        frame = tk.Frame(parent, bg=color, width=250, height=70)
        frame.pack(side="left", padx=10)

        tk.Label(frame,
                 text=title,
                 bg=color,
                 fg="white",
                 font=("Segoe UI", 10)).pack()

        value = tk.Label(frame,
                         text="0",
                         bg=color,
                         fg="white",
                         font=("Segoe UI", 16, "bold"))

        value.pack()

        return value

    # ================= LOAD ACCOUNTS =================
    def load_accounts(self):

        conn = self.get_connection()

        df = pd.read_sql(
            "SELECT DISTINCT Ac_Name FROM dbo.Dailytrans1",
            conn)

        conn.close()

        self.account_combo["values"] = ["All Accounts"] + df["Ac_Name"].tolist()
        self.account_combo.current(0)

    # ================= FETCH DATA =================
    def fetch_report(self, from_date, to_date, account):

        conn = self.get_connection()

        account_filter = ""

        if account != "All Accounts":
            account_filter = f" AND Ac_Name='{account}'"

        query = f"""
        SELECT 
            YEAR(Date1) Year,
            MONTH(Date1) Month,
            SUM(ISNULL(Debit,0)) Debit,
            SUM(ISNULL(Credit,0)) Credit
        FROM Dailytrans1
        WHERE Date1 BETWEEN '{from_date}' AND '{to_date}'
        {account_filter}
        GROUP BY YEAR(Date1), MONTH(Date1)
        ORDER BY Year, Month
        """

        df = pd.read_sql(query, conn)

        conn.close()

        return df

    # ================= LOAD REPORT =================
    def load_report(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        from_date = self.cal_from.get_date()
        to_date = self.cal_to.get_date()

        account = self.account_combo.get()

        df = self.fetch_report(from_date, to_date, account)

        if df.empty:
            messagebox.showinfo("Info", "No Data Found")
            return

        df["Month-Year"] = pd.to_datetime(
            df["Year"].astype(str) + "-" +
            df["Month"].astype(str) + "-01"
        ).dt.strftime("%b-%Y")

        df["Net"] = df["Debit"] - df["Credit"]

        self.df_report = df

        # -------- Fill Table --------
        for _, row in df.iterrows():

            self.tree.insert("",
                             "end",
                             values=(row["Month-Year"],
                                     row["Debit"],
                                     row["Credit"],
                                     row["Net"]))

        # -------- Update Cards --------
        self.card_debit.config(text=f"{df['Debit'].sum():,.2f}")
        self.card_credit.config(text=f"{df['Credit'].sum():,.2f}")
        self.card_profit.config(text=f"{df['Net'].sum():,.2f}")

        self.draw_chart(df)

    # ================= BAR CHART =================
    def draw_chart(self, df):

        fig, ax = plt.subplots(figsize=(7, 3))

        ax.bar(df["Month-Year"], df["Debit"], color="red", label="Debit")
        ax.bar(df["Month-Year"], df["Credit"], color="green", label="Credit")

        ax.set_title("Monthly Debit vs Credit")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= EXPORT EXCEL =================
    def export_excel(self):

        if self.df_report is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx")

        if path:
            self.df_report.to_excel(path, index=False)
            messagebox.showinfo("Saved", "Excel File Saved")

    # ================= EXPORT PDF =================
    def export_pdf(self):

        if self.df_report is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf")

        if not path:
            return

        data = [self.df_report.columns.tolist()] + \
               self.df_report.values.tolist()

        pdf = SimpleDocTemplate(path)

        table = Table(data)

        table.setStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ])

        pdf.build([table])

        messagebox.showinfo("Saved", "PDF Report Created")