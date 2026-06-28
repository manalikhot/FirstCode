import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc


class MemberForm:

    # ================= INIT =================
    def __init__(self, parent):

        self.parent = parent
        self.frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        self.marathi_font = ("Nirmala UI", 12)

        # -------- VARIABLES --------
        self.flat_no = tk.StringVar()
        self.name = tk.StringVar()
        self.address = tk.StringVar()
        self.mob1 = tk.StringVar()
        self.mob2 = tk.StringVar()
        self.email = tk.StringVar()
        self.search_var = tk.StringVar()

        self.create_widgets()
        self.fetch_data()

    # ================= DATABASE =================
    def get_connection(self):
        try:
            return pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=Sarthak;"
                "DATABASE=Socity_db;"
                "Trusted_Connection=yes;"
            )
        except Exception as e:
            messagebox.showerror("डेटाबेस त्रुटी", str(e))
            return None

    # ================= UI =================
    def create_widgets(self):

        # ---------- HEADER ----------
        header = tk.Frame(self.frame, bg="#8df3cb", height=60)
        header.pack(fill="x")

        tk.Label(header,
                 text="सदस्य नोंदणी",
                 font=("Segoe UI", 18, "bold"),
                 bg="#8df3cb",
                 fg="blue").pack(side="left", padx=20)

        tk.Button(header,
                  text="बाहेर पडा",
                  bg="#e74c3c",
                  fg="white",
                  command=self.frame.destroy
                  ).pack(side="right", padx=20, pady=10)

        # ---------- FORM ----------
        form_frame = tk.LabelFrame(
            self.frame,
            text="सदस्य माहिती",
            font=("Segoe UI", 11, "bold"),
            bg="#ecf0f1",
            padx=20,
            pady=20
        )
        form_frame.pack(fill="x", padx=20, pady=20)

        labels = [
            ("फ्लॅट क्रमांक", self.flat_no),
            ("सदस्याचे नाव", self.name),
            ("पत्ता", self.address),
            ("मोबाईल क्रमांक 1", self.mob1),
            ("मोबाईल क्रमांक 2", self.mob2),
            ("ई-मेल", self.email)
        ]

        for i, (text, var) in enumerate(labels):

            tk.Label(form_frame,
                     text=text,
                     font=self.marathi_font,
                     bg="#ecf0f1").grid(row=i, column=0,
                                        padx=10, pady=8, sticky="e")

            entry = tk.Entry(form_frame,
                             textvariable=var,
                             font=self.marathi_font,
                             width=40)

            entry.grid(row=i, column=1, padx=10, pady=8)

            if i == 0:
                self.flat_entry = entry

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(self.frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="जोडा", width=12,
                  command=self.add_record,
                  bg="#2ecc71", fg="white").grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="सुधारा", width=12,
                  command=self.update_record,
                  bg="#3498db", fg="white").grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="काढून टाका", width=12,
                  command=self.delete_record,
                  bg="#e74c3c", fg="white").grid(row=0, column=2, padx=10)

        tk.Button(btn_frame, text="रिकामे करा", width=12,
                  command=self.clear_fields,
                  bg="#95a5a6", fg="white").grid(row=0, column=3, padx=10)

        # ---------- SEARCH ----------
        search_frame = tk.Frame(self.frame, bg="#ecf0f1")
        search_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(search_frame,
                 text="शोधा (फ्लॅट / नाव / मोबाईल):",
                 font=("Segoe UI", 11, "bold"),
                 bg="#ecf0f1").pack(side="left", padx=5)

        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                width=40)
        search_entry.pack(side="left", padx=10)
        search_entry.bind("<KeyRelease>", self.search_record)

        tk.Button(search_frame,
                  text="शोध साफ करा",
                  command=self.clear_search,
                  bg="orange").pack(side="left", padx=10)

        # ---------- TREEVIEW ----------
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("flat_no", "name", "address", "mob1", "mob2", "email")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("flat_no", text="फ्लॅट क्रमांक")
        self.tree.heading("name", text="सदस्य नाव")
        self.tree.heading("address", text="पत्ता")
        self.tree.heading("mob1", text="मोबाईल 1")
        self.tree.heading("mob2", text="मोबाईल 2")
        self.tree.heading("email", text="ई-मेल")

        self.tree.column("flat_no", width=100, anchor="center")
        self.tree.column("name", width=160)
        self.tree.column("address", width=250)
        self.tree.column("mob1", width=120)
        self.tree.column("mob2", width=120)
        self.tree.column("email", width=200)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ================= SELECT ROW =================
    def on_row_select(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(selected, "values")

        if len(values) != 6:
            return

        self.flat_no.set(values[0])
        self.name.set(values[1])
        self.address.set(values[2])
        self.mob1.set(values[3])
        self.mob2.set(values[4])
        self.email.set(values[5])

        self.flat_entry.config(state="disabled")

    # ================= ADD =================
    def add_record(self):

        if not self.flat_no.get().isdigit():
            messagebox.showwarning("इशारा", "फ्लॅट क्रमांक अंकामध्ये असावा")
            return

        conn = self.get_connection()
        if not conn:
            return

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO Member_Mast
        VALUES (?,?,?,?,?,?)
        """, (
            int(self.flat_no.get()),
            self.name.get(),
            self.address.get(),
            self.mob1.get(),
            self.mob2.get(),
            self.email.get()
        ))

        conn.commit()
        conn.close()

        self.fetch_data()
        self.clear_fields()

        messagebox.showinfo("यशस्वी", "नोंद यशस्वीरीत्या जोडली")

    # ================= UPDATE =================
    def update_record(self):

        selected = self.tree.focus()

        if not selected:
            messagebox.showwarning("इशारा", "अपडेट करण्यासाठी रेकॉर्ड निवडा")
            return

        conn = self.get_connection()

        try:
            cur = conn.cursor()

            cur.execute("""
            UPDATE Member_Mast
            SET Member_name=?,
                Member_Add=?,
                Member_mob1=?,
                Member_mob2=?,
                Member_email=?
            WHERE flat_no=?
            """, (
                self.name.get(),
                self.address.get(),
                self.mob1.get(),
                self.mob2.get(),
                self.email.get(),
                int(self.flat_no.get())
            ))

            conn.commit()

            messagebox.showinfo("यशस्वी", "रेकॉर्ड अपडेट झाला")

            self.fetch_data()
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("त्रुटी", str(e))

        finally:
            conn.close()
        # ================= DELETE =================
    def delete_record(self):

        selected = self.tree.focus()

        if not selected:
            messagebox.showwarning("इशारा", "काढण्यासाठी रेकॉर्ड निवडा")
            return

        confirm = messagebox.askyesno("खात्री", "ही नोंद काढायची का?")
        if not confirm:
            return

        conn = self.get_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("""
            DELETE FROM Member_Mast
            WHERE flat_no=?
            """, (int(self.flat_no.get()),))

            conn.commit()

            messagebox.showinfo("यशस्वी", "नोंद काढली")

            self.fetch_data()
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("त्रुटी", str(e))

        finally:
            conn.close()
        # ================= CLEAR =================
    def clear_fields(self):

        self.flat_no.set("")
        self.name.set("")
        self.address.set("")
        self.mob1.set("")
        self.mob2.set("")
        self.email.set("")

        self.flat_entry.config(state="normal")

        # remove tree selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
            
    # ================= FETCH =================
    def fetch_data(self):

        conn = self.get_connection()
        if not conn:
            return

        cur = conn.cursor()

        cur.execute("""
        SELECT flat_no, Member_name, Member_Add,
               Member_mob1, Member_mob2, Member_email
        FROM Member_Mast
        ORDER BY flat_no
        """)

        rows = cur.fetchall()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2],
                row[3], row[4], row[5]
            ))

        conn.close()

    # ================= SEARCH =================
    def search_record(self, event=None):

        conn = self.get_connection()
        if not conn:
            return

        cur = conn.cursor()

        search_text = self.search_var.get()

        query = """
        SELECT flat_no, Member_name, Member_Add,
               Member_mob1, Member_mob2, Member_email
        FROM Member_Mast
        WHERE CAST(flat_no AS NVARCHAR) LIKE ?
        OR Member_name LIKE ?
        OR Member_mob1 LIKE ?
        """

        param = f"%{search_text}%"

        cur.execute(query, (param, param, param))
        rows = cur.fetchall()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2],
                row[3], row[4], row[5]
            ))

        conn.close()

    def clear_search(self):
        self.search_var.set("")
        self.fetch_data()


# ================= MAIN =================
if __name__ == "__main__":

    root = tk.Tk()
    root.title("Member Registration")
    root.geometry("900x600")

    app = MemberForm(root)

    root.mainloop()