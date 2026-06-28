import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc


class OpeningBalanceEntry:

    def __init__(self, parent):

        self.win = tk.Toplevel(parent)
        self.win.title("Opening Balance Entry")
        self.win.geometry("700x450")

        self.center_window()

        # -------------------------
        # DATABASE CONNECTION
        # -------------------------
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

        self.cursor = self.conn.cursor()

        self.create_widgets()
        self.load_data()

    # -------------------------
    # CENTER WINDOW
    # -------------------------
    def center_window(self):

        self.win.update_idletasks()

        width = 700
        height = 450

        x = (self.win.winfo_screenwidth() // 2) - (width // 2)
        y = (self.win.winfo_screenheight() // 2) - (height // 2)

        self.win.geometry(f"{width}x{height}+{x}+{y}")

    # -------------------------
    # CREATE UI
    # -------------------------
    def create_widgets(self):

        form = tk.Frame(self.win)
        form.pack(pady=10)

        tk.Label(form,text="Flat No").grid(row=0,column=0,padx=10,pady=5)
        tk.Label(form,text="Year").grid(row=1,column=0,padx=10,pady=5)
        tk.Label(form,text="Debit").grid(row=2,column=0,padx=10,pady=5)
        tk.Label(form,text="Credit").grid(row=3,column=0,padx=10,pady=5)

        self.txt_flat = tk.Entry(form)
        self.txt_year = tk.Entry(form)
        self.txt_debit = tk.Entry(form)
        self.txt_credit = tk.Entry(form)

        self.txt_flat.grid(row=0,column=1)
        self.txt_year.grid(row=1,column=1)
        self.txt_debit.grid(row=2,column=1)
        self.txt_credit.grid(row=3,column=1)

        # -------------------------
        # BUTTONS
        # -------------------------
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,text="Save",width=10,
                  command=self.save_data).grid(row=0,column=0,padx=10)

        tk.Button(btn_frame,text="Update",width=10,
                  command=self.update_data).grid(row=0,column=1,padx=10)

        tk.Button(btn_frame,text="Clear",width=10,
                  command=self.clear_form).grid(row=0,column=2,padx=10)

        tk.Button(btn_frame,text="Exit",width=10,
                  command=self.win.destroy).grid(row=0,column=3,padx=10)

        # -------------------------
        # TREEVIEW
        # -------------------------
        table_frame = tk.Frame(self.win)
        table_frame.pack(fill="both",expand=True,padx=10,pady=10)

        self.tree = ttk.Treeview(table_frame)

        self.tree["columns"] = ("Flat_No","Year","Debit","Credit")

        self.tree["show"] = "headings"

        for col in self.tree["columns"]:
            self.tree.heading(col,text=col)
            self.tree.column(col,width=120)

        self.tree.pack(fill="both",expand=True)

        self.tree.bind("<ButtonRelease-1>", self.select_record)
#profestional Tree view
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial",10,"bold"))
        style.configure("Treeview", rowheight=24, font=("Arial",10))

        self.tree.column("Debit",anchor="e")
        self.tree.column("Credit",anchor="e")

    # -------------------------
    # LOAD DATA
    # -------------------------
    def load_data(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("""
        SELECT Flat_No,Year,Debit,Credit
        FROM Opening_Balance
        ORDER BY Flat_No
        """)

        rows = self.cursor.fetchall()

        for r in rows:

            flat = r[0]
            year = r[1]
            debit = float(r[2]) if r[2] else 0
            credit = float(r[3]) if r[3] else 0

            self.tree.insert(
            "",
            tk.END,
            values=(
                flat,
                year,
                f"{debit:.2f}",
                f"{credit:.2f}"
            )
        )

    # -------------------------
    # SAVE DATA
    # -------------------------
    def save_data(self):

        flat = self.txt_flat.get()
        year = self.txt_year.get()
        debit = self.txt_debit.get()
        credit = self.txt_credit.get()

        self.cursor.execute("""
        INSERT INTO Opening_Balance
        (Flat_No,Year,Debit,Credit)
        VALUES (?,?,?,?)
        """,(flat,year,debit,credit))

        self.conn.commit()

        messagebox.showinfo("Saved","Record Saved Successfully")

        self.load_data()
        self.clear_form()

    # -------------------------
    # UPDATE DATA
    # -------------------------
    def update_data(self):

        flat = self.txt_flat.get()
        year = self.txt_year.get()
        debit = self.txt_debit.get()
        credit = self.txt_credit.get()

        self.cursor.execute("""
        UPDATE Opening_Balance
        SET Debit=?, Credit=?
        WHERE Flat_No=? AND Year=?
        """,(debit,credit,flat,year))

        self.conn.commit()

        messagebox.showinfo("Updated","Record Updated Successfully")

        self.load_data()

    # -------------------------
    # SELECT RECORD
    # -------------------------
    def select_record(self,event):

        selected = self.tree.focus()

        values = self.tree.item(selected,"values")

        if values:

            self.clear_form()

            self.txt_flat.insert(0,values[0])
            self.txt_year.insert(0,values[1])
            self.txt_debit.insert(0,values[2])
            self.txt_credit.insert(0,values[3])

    # -------------------------
    # CLEAR FORM
    # -------------------------
    def clear_form(self):

        self.txt_flat.delete(0,tk.END)
        self.txt_year.delete(0,tk.END)
        self.txt_debit.delete(0,tk.END)
        self.txt_credit.delete(0,tk.END)