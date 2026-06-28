import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from tkcalendar import DateEntry


class DailyExpenseForm:

    # ================= सुरुवात =================
    def __init__(self, parent):

        self.parent = parent
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        self.selected_id = None

        self.create_widgets()
        self.load_members()
        self.load_data()
        self.auto_fill_year_month()

    # ================= DATABASE =================
    def connect_db(self):
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= UI =================
    def create_widgets(self):

        # ---------- हेडर ----------
        header = tk.Frame(self.frame, bg="#8df3cb", height=60)
        header.pack(fill="x")

        tk.Label(header,
                 text="दैनंदिन खर्च नोंद",
                 font=("Segoe UI", 18, "bold"),
                 bg="#8df3cb",
                 fg="blue").pack(side="left", padx=20)

        tk.Button(header,
                  text="बंद करा",
                  bg="#e74c3c",
                  fg="white",
                  command=self.frame.destroy
                  ).pack(side="right", padx=20, pady=10)

        # ---------- नोंद फ्रेम ----------
        entry_frame = tk.LabelFrame(
            self.frame,
            text="नोंद तपशील",
            bg="#9dece5",
            font=("Segoe UI", 10, "bold")
        )
        entry_frame.pack(fill="x", padx=15, pady=10)

        # पहिली ओळ
        tk.Label(entry_frame, text="दिनांक", bg="#9dece5").grid(row=0, column=0)
        self.date_entry = DateEntry(entry_frame, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1)
        self.date_entry.bind("<<DateEntrySelected>>", self.auto_fill_year_month)

        tk.Label(entry_frame, text="वर्ष", bg="#9dece5").grid(row=0, column=2)
        self.year_combo = ttk.Combobox(entry_frame, width=8, state="readonly",
                                       values=["2024", "2025", "2026"])
        self.year_combo.grid(row=0, column=3)

        tk.Label(entry_frame, text="महिना", bg="#9dece5").grid(row=0, column=4)
        self.month_combo = ttk.Combobox(entry_frame, width=12, state="readonly",
                                        values=["January", "February", "March", "April",
                                                "May", "June", "July", "August",
                                                "September", "October", "November", "December"])
        self.month_combo.grid(row=0, column=5)

        tk.Label(entry_frame, text="सभासद", bg="#9dece5").grid(row=0, column=6)
        self.member_combo = ttk.Combobox(entry_frame, width=18, state="readonly")
        self.member_combo.grid(row=0, column=7)
        self.member_combo.bind("<<ComboboxSelected>>", self.on_member_selected)

        tk.Label(entry_frame, text="फ्लॅट", bg="#9dece5").grid(row=0, column=8)
        self.flat_entry = tk.Entry(entry_frame, width=10)
        self.flat_entry.grid(row=0, column=9)

        # दुसरी ओळ
        tk.Label(entry_frame, text="सब खाते", bg="#9dece5").grid(row=1, column=0)
        self.subac_combo = ttk.Combobox(entry_frame, width=18, state="readonly")
        self.subac_combo.grid(row=1, column=1)

        tk.Label(entry_frame, text="तपशील", bg="#9dece5").grid(row=1, column=2)
        self.detail_entry = tk.Entry(entry_frame, width=30)
        self.detail_entry.grid(row=1, column=3)

        tk.Label(entry_frame, text="डेबिट", bg="#9dece5").grid(row=1, column=4)
        self.debit_entry = tk.Entry(entry_frame, width=12)
        self.debit_entry.grid(row=1, column=5)
        self.debit_entry.bind("<KeyRelease>", self.auto_balance)

        tk.Label(entry_frame, text="क्रेडिट", bg="#9dece5").grid(row=1, column=6)
        self.credit_entry = tk.Entry(entry_frame, width=12)
        self.credit_entry.grid(row=1, column=7)
        self.credit_entry.bind("<KeyRelease>", self.auto_balance)

        # ---------- ट्रीव्ह्यू ----------
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "दिनांक", "वर्ष", "महिना", "सभासद",
                   "फ्लॅट", "सब खाते", "तपशील",
                   "डेबिट", "क्रेडिट", "बॅलन्स")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.edit_record)

        # ---------- एकूण ----------
        footer = tk.Frame(self.frame, bg="#ecf0f1")
        footer.pack(fill="x")

        self.total_debit_label = tk.Label(
            footer,
            text="एकूण डेबिट: 0.00",
            font=("Segoe UI", 12, "bold"),
            fg="green"
        )
        self.total_debit_label.pack(side="left", padx=20)

        self.total_credit_label = tk.Label(
            footer,
            text="एकूण क्रेडिट: 0.00",
            font=("Segoe UI", 12, "bold"),
            fg="red"
        )
        self.total_credit_label.pack(side="left", padx=20)

        # ---------- बटण ----------
        btn_frame = tk.Frame(self.frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="जतन करा",
                  bg="green", fg="white",
                  command=self.save_data).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="अपडेट करा",
                  bg="blue", fg="white",
                  command=self.update_data).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="डिलीट करा",
                  bg="red", fg="white",
                  command=self.delete_data).grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="सर्व दाखवा",
                  bg="orange",
                  command=self.load_data).grid(row=0, column=3, padx=5)

    # ================= बाकी सर्व DATABASE & LOGIC FUNCTIONS =================
    # (तुमच्या मूळ कोड प्रमाणेच – save, update, delete, load_data, load_members etc.)
    # ================= AUTO YEAR & MONTH =================
    def auto_fill_year_month(self, event=None):
        date = self.date_entry.get_date()
        self.year_combo.set(str(date.year))
        self.month_combo.set(date.strftime("%B"))

    # ================= AUTO BALANCE =================
    def auto_balance(self, event=None):
        if event.widget == self.debit_entry and self.debit_entry.get():
            self.credit_entry.delete(0, tk.END)

        if event.widget == self.credit_entry and self.credit_entry.get():
            self.debit_entry.delete(0, tk.END)

    # ================= LOAD MEMBERS =================
    def load_members(self):
        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT Member_Name
        FROM dbo.Member_Mast
        ORDER BY Member_Name
        """)

        rows = cursor.fetchall()
        self.member_combo["values"] = [r[0] for r in rows]

        conn.close()
        # ================= FILL MEMBER DETAILS =================
    def fill_member_details(self, event=None):

        member_name = self.member_combo.get()

        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Flat_No, Subac_Name
            FROM dbo.SubMember_Mast
            WHERE Member_Name = ?
            ORDER BY Subac_Name
            """, member_name)

        rows = cursor.fetchall()

        if rows:
        # Set Flat No (same for all subaccounts)
            self.flat_entry.delete(0, tk.END)
            self.flat_entry.insert(0, rows[0][0])

        # Load all subaccounts into combobox
            subaccounts = [r[1] for r in rows]
            self.subac_combo["values"] = subaccounts
            self.subac_combo.set(subaccounts[0])  # default select first

        else:
            self.flat_entry.delete(0, tk.END)
            self.subac_combo["values"] = []
            self.subac_combo.set("")

        conn.close()
    # ================= LOAD DATA =================
    def load_data(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ID, Date1, Pyear, Pmonth,
                   Ac_Name, Flat_No, Subac_Name,
                   Particulars, Debit, Credit
            FROM dbo.Dailytrans1
            ORDER BY Date1 ASC, ID ASC
        """)

        rows = cursor.fetchall()

        total_debit = total_credit = running_balance = 0

        for row in rows:
            debit = float(row[8] or 0)
            credit = float(row[9] or 0)

            #running_balance += debit - credit
            running_balance += credit - debit
            total_debit += debit
            total_credit += credit

            self.tree.insert("", "end", values=(
                row[0],
                row[1].strftime("%Y-%m-%d"),
                row[2], row[3],
                row[4], row[5],
                row[6], row[7],
                f"{debit:.2f}",
                f"{credit:.2f}",
                f"{running_balance:.2f}"
            ))

        conn.close()

        self.total_debit_label.config(text=f"Total Debit: {total_debit:.2f}")
        self.total_credit_label.config(text=f"Total Credit: {total_credit:.2f}")

    # ================= EDIT =================
    def edit_record(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, "values")
        self.selected_id = values[0]

        self.date_entry.set_date(values[1])
        self.year_combo.set(values[2])
        self.month_combo.set(values[3])
        self.member_combo.set(values[4])

        self.flat_entry.delete(0, tk.END)
        self.flat_entry.insert(0, values[5])

        self.subac_combo.set(values[6])

        self.detail_entry.delete(0, tk.END)
        self.detail_entry.insert(0, values[7])

        self.debit_entry.delete(0, tk.END)
        self.debit_entry.insert(0, values[8])

        self.credit_entry.delete(0, tk.END)
        self.credit_entry.insert(0, values[9])

    # ================= CLEAR FORM =================
    def clear_form(self):
        self.selected_id = None
        self.detail_entry.delete(0, tk.END)
        self.debit_entry.delete(0, tk.END)
        self.credit_entry.delete(0, tk.END)

    # ================= SAVE =================
    def save_data(self):
        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO dbo.Dailytrans1
            (Date1, Pyear, Pmonth, Ac_Name,
             Flat_No, Subac_Name, Particulars,
             Debit, Credit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
                       self.date_entry.get(),
                       self.year_combo.get(),
                       self.month_combo.get(),
                       self.member_combo.get(),
                       self.flat_entry.get(),
                       self.subac_combo.get(),
                       self.detail_entry.get(),
                       float(self.debit_entry.get() or 0),
                       float(self.credit_entry.get() or 0))

        conn.commit()
        conn.close()

        self.clear_form()
        self.load_data()

    # ================= UPDATE =================
    def update_data(self):
        if not self.selected_id:
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE dbo.Dailytrans1
            SET Date1=?, Pyear=?, Pmonth=?,
                Ac_Name=?, Flat_No=?,
                Subac_Name=?, Particulars=?,
                Debit=?, Credit=?
            WHERE ID=?
        """,
                       self.date_entry.get(),
                       self.year_combo.get(),
                       self.month_combo.get(),
                       self.member_combo.get(),
                       self.flat_entry.get(),
                       self.subac_combo.get(),
                       self.detail_entry.get(),
                       float(self.debit_entry.get() or 0),
                       float(self.credit_entry.get() or 0),
                       self.selected_id)

        conn.commit()
        conn.close()

        self.clear_form()
        self.load_data()

    # ================= DELETE =================
    def delete_data(self):
        selected = self.tree.focus()
        if not selected:
            return

        record_id = self.tree.item(selected, "values")[0]

        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.Dailytrans1 WHERE ID=?", record_id)
        conn.commit()
        conn.close()

        self.load_data()

    def on_member_selected(self, event=None):
        self.fill_member_details()
        self.load_data_by_member()
    
    def load_data_by_member(self):

        selected_member = self.member_combo.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT ID, Date1, Pyear, Pmonth,
               Ac_Name, Flat_No, Subac_Name,
               Particulars, Debit, Credit
        FROM dbo.Dailytrans1
        WHERE Ac_Name = ?
        ORDER BY Date1 ASC, ID ASC
        """, selected_member)

        rows = cursor.fetchall()

        total_debit = total_credit = running_balance = 0

        for row in rows:
            debit = float(row[8] or 0)
            credit = float(row[9] or 0)

            #running_balance += debit - credit
            running_balance += credit - debit
            total_debit += debit
            total_credit += credit

            self.tree.insert("", "end", values=(
            row[0],
            row[1].strftime("%Y-%m-%d"),
            row[2], row[3],
            row[4], row[5],
            row[6], row[7],
            f"{debit:.2f}",
            f"{credit:.2f}",
            f"{running_balance:.2f}"
        ))

        conn.close()

        self.total_debit_label.config(text=f"Total Debit: {total_debit:.2f}")
        self.total_credit_label.config(text=f"Total Credit: {total_credit:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DailyExpenseForm(root)
    root.mainloop()
