import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading

from Master_Entry import MemberForm
from Sub_Master import SubMemberMaster
from opening_balance_entry import OpeningBalanceEntry
from daily_expense_form import DailyExpenseForm
from MonthlySummery import MonthSummaryForm
from month_wise_dashboard import MonthWiseDashboard
from monthwise_pending_report import MonthwisePendingReport
from Society_Month_total import MonthTotalReport
from Socity_MonthWise_Payment_Report import MonthWisePaymentReport
from Socity_MonthWise_Pending_report import MonthPendingReport
from ServerBackup import SQLBackupApp

import pyodbc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw


class MainMenu:

    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard")

        try:
            self.root.state("zoomed")
        except:
            self.root.attributes("-zoomed", True)

        self.sidebar_bg = "#273746"
        self.submenu_bg = "#34495e"
        self.header_bg = "#1f2c40"
        self.content_bg = "#ecf0f1"

        self.create_layout()

    # ================= DATABASE =================
    def get_connection(self):
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= IMAGE =================
    def create_circular_image(self, image_path, size=(150, 150)):
        try:
            img = Image.open(image_path).resize(size, Image.LANCZOS)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("Image Error:", e)
            return None

    # ================= LAYOUT =================
    def create_layout(self):

        header = tk.Frame(self.root, bg=self.header_bg, height=60)
        header.pack(side="top", fill="x")

        tk.Label(header, text="SOCIETY MANAGEMENT SYSTEM",
                 bg=self.header_bg, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)

        tk.Button(header, text="Logout", bg="red", fg="white",
                  width=10, command=self.logout).pack(side="right", padx=20, pady=10)

        body = tk.Frame(self.root)
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=self.sidebar_bg, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg=self.content_bg)
        self.content.pack(side="right", fill="both", expand=True)

        self.create_sidebar_menu()
        self.show_home()

    # ================= SIDEBAR =================
    def create_sidebar_menu(self):

        self.menu_button("🏠 Dashboard", self.show_home)

        # MASTER
        self.menu_button("📁 Master", self.toggle_master_menu)
        self.master_submenu = tk.Frame(self.sidebar, bg=self.submenu_bg)
        self.submenu_button(self.master_submenu, "Main Account", self.open_main_account)
        self.submenu_button(self.master_submenu, "Sub Account", self.open_sub_account)
        self.submenu_button(self.master_submenu, "Opening Balance Entry", self.open_Balance_entry)

        # TRANSACTION
        self.menu_button("💰 Transaction", self.toggle_transaction_menu)
        self.transaction_submenu = tk.Frame(self.sidebar, bg=self.submenu_bg)
        self.submenu_button(self.transaction_submenu, "Daily Expense Entry", self.open_daily_expense)

        # REPORT
        self.menu_button("📊 Reports", self.toggle_report_menu)
        self.report_submenu = tk.Frame(self.sidebar, bg=self.submenu_bg)
        self.submenu_button(self.report_submenu, "Monthly Summary", self.open_monthly_summary)
        self.submenu_button(self.report_submenu, "Month Wise Report", self.open_monthly_report)
        self.submenu_button(self.report_submenu, "Pending Report", self.open_pending_report)
        self.submenu_button(self.report_submenu, "Month Total", self.open_month_total)
        self.submenu_button(self.report_submenu, "Month Wise Payment", self.month_Payment_total)
        self.submenu_button(self.report_submenu, "Month Wise Pending", self.month_pending)

        # UTILITY
        self.menu_button("🛠 Utility", self.toggle_utility_menu)
        self.utility_submenu = tk.Frame(self.sidebar, bg=self.submenu_bg)
        self.submenu_button(self.utility_submenu, "💾 Database Backup", self.open_backup_tool)

        # EXIT
        self.menu_button("❌ Exit", self.root.destroy)

    def menu_button(self, text, command):
        tk.Button(self.sidebar, text=text, anchor="w",
                  bg=self.sidebar_bg, fg="white", bd=0,
                  pady=12, font=("Segoe UI", 12),
                  command=command).pack(fill="x")

    def submenu_button(self, parent, text, command):
        tk.Button(parent, text="   " + text, anchor="w",
                  bg=self.submenu_bg, fg="white", bd=0,
                  pady=8, font=("Segoe UI", 11),
                  command=command).pack(fill="x")

    def close_all_submenus(self):
        self.master_submenu.pack_forget()
        self.transaction_submenu.pack_forget()
        self.report_submenu.pack_forget()
        self.utility_submenu.pack_forget()
    def toggle_master_menu(self):
        self.close_all_submenus()
        self.master_submenu.pack(fill="x")

    def toggle_transaction_menu(self):
        self.close_all_submenus()
        self.transaction_submenu.pack(fill="x")

    def toggle_report_menu(self):
        self.close_all_submenus()
        self.report_submenu.pack(fill="x")

    def toggle_utility_menu(self):
        self.close_all_submenus()
        self.utility_submenu.pack(fill="x")

    # ================= DASHBOARD =================
    def show_home(self):
        self.clear_content()

        tk.Label(self.content, text="Loading Dashboard...",
                 font=("Segoe UI", 20, "bold"),
                 bg=self.content_bg).pack(pady=100)

        threading.Thread(target=self.load_dashboard_data, daemon=True).start()

    def load_dashboard_data(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Member_Mast")
            members = cursor.fetchone()[0] or 0

            cursor.execute("SELECT ISNULL(SUM(Debit),0), ISNULL(SUM(Credit),0) FROM Dailytrans1")
            debit, credit = cursor.fetchone()

            balance = credit - debit

            cursor.execute("""
                SELECT CONVERT(VARCHAR(7), Date1, 120),
                       ISNULL(SUM(Debit),0),
                       ISNULL(SUM(Credit),0)
                FROM Dailytrans1
                GROUP BY CONVERT(VARCHAR(7), Date1, 120)
                ORDER BY 1
            """)

            rows = cursor.fetchall()
            conn.close()

            months, d_data, c_data = [], [], []

            for r in rows:
                months.append(r[0])
                d_data.append(float(r[1]))
                c_data.append(float(r[2]))

            self.root.after(0, lambda: self.display_dashboard(
                members, debit, credit, balance, months, d_data, c_data
            ))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def display_dashboard(self, members, debit, credit, balance, months, d_data, c_data):
        self.clear_content()

        img = self.create_circular_image(r"D:\PythonProject\Saikrupa\building.jpg", (160, 160))
        lbl = tk.Label(self.content, image=img, bg=self.content_bg)
        lbl.image = img
        lbl.pack(pady=10)

        tk.Label(self.content,
                 text="साईकृपा सोसायटी व्यवस्थापन डॅशबोर्ड",
                 font=("Segoe UI", 30, "bold"),
                 bg=self.content_bg).pack(pady=10)

        frame = tk.Frame(self.content, bg=self.content_bg)
        frame.pack(pady=15)

        self.create_card(frame, "सभासद", members, "#3498db", 0)
        self.create_card(frame, "खर्च", f"₹ {debit:,.2f}", "#e74c3c", 1)
        self.create_card(frame, "जमा", f"₹ {credit:,.2f}", "#2ecc71", 2)
        self.create_card(frame, "शिल्लक", f"₹ {balance:,.2f}", "#9b59b6", 3)

        chart_frame = tk.Frame(self.content, bg="white")
        chart_frame.pack(fill="both", expand=True, padx=40, pady=20)

        fig = plt.Figure(figsize=(12, 5), dpi=100)

        ax1 = fig.add_subplot(121)
        x = range(len(months))
        ax1.bar(x, d_data, width=0.4, label="Debit")
        ax1.bar([i + 0.4 for i in x], c_data, width=0.4, label="Credit")
        ax1.set_xticks([i + 0.2 for i in x])
        ax1.set_xticklabels(months, rotation=45)
        ax1.legend()

        ax2 = fig.add_subplot(122)
        ax2.pie([debit, credit], labels=["Debit", "Credit"], autopct="%1.1f%%")

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_card(self, parent, title, value, color, col):

        card = tk.Frame(parent, bg=color, width=180, height=110)
        card.grid(row=0, column=col, padx=20, pady=10)

    # IMPORTANT: Prevent auto shrink
        card.grid_propagate(False)

    # TITLE (Top Text)
        title_label = tk.Label(
        card,
        text=title,
        bg=color,
        fg="white",
        font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(12, 5))

    # VALUE (Main Big Number)
        value_label = tk.Label(
        card,
        text=value,
        bg=color,
        fg="white",
        font=("Arial", 18, "bold")
        )
        value_label.pack(pady=(0, 10))

    def clear_content(self):
            for w in self.content.winfo_children():
                w.destroy()

    # ================= FORMS =================
    def open_main_account(self):
        self.clear_content()
        MemberForm(self.content)

    def open_sub_account(self):
        self.clear_content()
        SubMemberMaster(self.content)

    def open_Balance_entry(self):
        self.clear_content()
        OpeningBalanceEntry(self.content)

    def open_daily_expense(self):
        self.clear_content()
        DailyExpenseForm(self.content)

    def open_monthly_summary(self):
        self.clear_content()
        MonthSummaryForm(self.content)

    def open_monthly_report(self):
        self.clear_content()
        MonthWiseDashboard(self.content)

    def open_pending_report(self):
        self.clear_content()
        MonthwisePendingReport(self.content)

    def open_month_total(self):
        self.clear_content()
        MonthTotalReport(self.content)

    def month_Payment_total(self):
        self.clear_content()
        MonthWisePaymentReport(self.content)

    def month_pending(self):
        self.clear_content()
        MonthPendingReport(self.content)

    # ================= BACKUP =================
    def open_backup_tool(self):
        self.clear_content()

        container = tk.Frame(self.content, bg=self.content_bg)
        container.pack(expand=True)

        tk.Label(container, text="Database Backup Utility",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.content_bg).pack(pady=20)

        progress = ttk.Progressbar(container, length=400)
        progress.pack(pady=20)

        status = tk.Label(container, text="", bg=self.content_bg)
        status.pack()

        def run_backup():
            for i in range(0, 101, 20):
                time.sleep(0.5)
                progress["value"] = i
                self.root.update_idletasks()

            SQLBackupApp(self.content)
            status.config(text="Backup Completed ✅")

        tk.Button(container, text="Start Backup",
                  command=lambda: threading.Thread(target=run_backup, daemon=True).start()
                  ).pack(pady=20)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()