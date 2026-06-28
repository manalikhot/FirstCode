import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pyodbc
import pandas as pd
from datetime import datetime
import threading

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ReportLab PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes


# ================= MAIN APPLICATION =================
class SocietyApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Society Management System")
        self.root.state("zoomed")

        # Modern Colors
        self.sidebar_bg = "#1f2933"
        self.sidebar_hover = "#323f4b"
        self.header_bg = "#111827"
        self.content_bg = "#f3f4f6"
        self.card_colors = ["#2563eb", "#dc2626", "#16a34a", "#7c3aed"]

        self.create_layout()

    # ================= DATABASE =================
    def get_connection(self):
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= LAYOUT =================
    def create_layout(self):

        header = tk.Frame(self.root, bg=self.header_bg, height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🏢 SOCIETY MANAGEMENT SYSTEM",
            fg="white",
            bg=self.header_bg,
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20)

        tk.Button(
            header,
            text="Logout",
            bg="red",
            fg="white",
            command=self.root.destroy
        ).pack(side="right", padx=20, pady=10)

        body = tk.Frame(self.root)
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=self.sidebar_bg, width=220)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(body, bg=self.content_bg)
        self.content.pack(side="right", fill="both", expand=True)

        self.create_sidebar()

        self.show_dashboard()

    # ================= SIDEBAR =================
    def create_sidebar(self):

        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📊 Reports Dashboard", self.open_monthwise_dashboard),
            ("❌ Exit", self.root.destroy)
        ]

        for text, command in buttons:
            btn = tk.Button(
                self.sidebar,
                text=text,
                bg=self.sidebar_bg,
                fg="white",
                bd=0,
                anchor="w",
                font=("Segoe UI", 12),
                pady=12,
                command=command
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.sidebar_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.sidebar_bg))

    # ================= DASHBOARD =================
    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.content, text="Loading Dashboard...",
                 font=("Segoe UI", 20, "bold"),
                 bg=self.content_bg).pack(pady=50)

        threading.Thread(target=self.load_dashboard_data, daemon=True).start()

    def load_dashboard_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Member_Mast")
        members = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT ISNULL(SUM(Debit),0), ISNULL(SUM(Credit),0)
            FROM Dailytrans1
        """)
        debit, credit = cursor.fetchone()
        balance = credit - debit

        conn.close()

        self.root.after(0, lambda:
            self.display_dashboard(members, debit, credit, balance)
        )

    def display_dashboard(self, members, debit, credit, balance):

        self.clear_content()

        title = tk.Label(
            self.content,
            text="📊 Financial Overview",
            font=("Segoe UI", 26, "bold"),
            bg=self.content_bg
        )
        title.pack(pady=20)

        card_frame = tk.Frame(self.content, bg=self.content_bg)
        card_frame.pack(pady=20)

        cards = [
            ("Total Members", members),
            ("Total Debit", f"₹ {debit:,.2f}"),
            ("Total Credit", f"₹ {credit:,.2f}"),
            ("Balance", f"₹ {balance:,.2f}")
        ]

        for i, (title, value) in enumerate(cards):
            self.create_card(card_frame, title, value, self.card_colors[i], i)

    def create_card(self, parent, title, value, color, col):
        frame = tk.Frame(parent, bg=color, width=250, height=130)
        frame.grid(row=0, column=col, padx=20)
        frame.grid_propagate(False)

        tk.Label(frame, text=title, bg=color,
                 fg="white", font=("Segoe UI", 14)).pack(pady=15)
        tk.Label(frame, text=value, bg=color,
                 fg="white", font=("Segoe UI", 18, "bold")).pack()

    # ================= MONTH WISE DASHBOARD =================
    def open_monthwise_dashboard(self):
        self.clear_content()
        MonthWiseDashboard(self.content, self.get_connection)

    # ================= UTIL =================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()


# ================= MONTHWISE REPORT CLASS =================
class MonthWiseDashboard(tk.Frame):

    def __init__(self, parent, connection_func):
        super().__init__(parent, bg="#f3f4f6")
        self.pack(fill="both", expand=True)
        self.get_connection = connection_func
        self.create_widgets()

    def create_widgets(self):

        filter_frame = tk.LabelFrame(self, text="Filters", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(filter_frame, text="From Date").grid(row=0, column=0)
        self.cal_from = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        self.cal_from.grid(row=0, column=1)

        tk.Label(filter_frame, text="To Date").grid(row=0, column=2)
        self.cal_to = DateEntry(filter_frame, date_pattern="dd-mm-yyyy")
        self.cal_to.grid(row=0, column=3)

        tk.Button(filter_frame, text="Load Report",
                  command=self.load_report).grid(row=0, column=4, padx=10)

        tk.Button(filter_frame, text="Export PDF",
                  command=self.save_pdf).grid(row=0, column=5)

        columns = ("Month", "Debit", "Credit", "Net")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill="x", padx=20, pady=10)

        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= LOAD REPORT =================
    def load_report(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        conn = self.get_connection()
        from_date = self.cal_from.get_date()
        to_date = self.cal_to.get_date()

        query = """
        SELECT YEAR(Date1) AS Year,
               MONTH(Date1) AS Month,
               SUM(ISNULL(Debit,0)) AS Debit,
               SUM(ISNULL(Credit,0)) AS Credit
        FROM Dailytrans1
        WHERE Date1 BETWEEN ? AND ?
        GROUP BY YEAR(Date1), MONTH(Date1)
        ORDER BY Year, Month
        """

        df = pd.read_sql(query, conn, params=[from_date, to_date])
        conn.close()

        if df.empty:
            messagebox.showinfo("Info", "No Data Found")
            return

        df["Month"] = pd.to_datetime(
            df["Year"].astype(str) + "-" +
            df["Month"].astype(str) + "-01"
        ).dt.strftime("%b-%Y")

        df["Net"] = df["Credit"] - df["Debit"]

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row["Month"],
                f"{row['Debit']:,.2f}",
                f"{row['Credit']:,.2f}",
                f"{row['Net']:,.2f}"
            ))

        self.draw_advanced_chart(df)
        self.current_df = df

    # ================= ADVANCED CHART =================
    def draw_advanced_chart(self, df):

        fig, ax = plt.subplots(figsize=(8,4))

        ax.bar(df["Month"], df["Debit"], label="Debit")
        ax.bar(df["Month"], df["Credit"], bottom=df["Debit"], label="Credit")

        ax.plot(df["Month"], df["Net"], marker="o")

        ax.set_title("Monthly Financial Performance")
        ax.legend()
        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= PDF EXPORT =================
    def save_pdf(self):

        if not hasattr(self, "current_df"):
            messagebox.showerror("Error", "Load report first")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Society Monthly Financial Report", styles["Heading1"]))
        elements.append(Spacer(1, 12))

        data = [["Month", "Debit", "Credit", "Net"]]

        for _, row in self.current_df.iterrows():
            data.append([
                row["Month"],
                f"{row['Debit']:,.2f}",
                f"{row['Credit']:,.2f}",
                f"{row['Net']:,.2f}"
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("ALIGN", (1,1), (-1,-1), "RIGHT")
        ]))

        elements.append(table)
        doc.build(elements)

        messagebox.showinfo("Success", "PDF Exported Successfully")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = SocietyApp(root)
    root.mainloop()