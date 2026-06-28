import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc


class SubMemberMaster:

    # ================= INIT =================
    def __init__(self, parent):

        self.parent = parent
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        self.marathi_font = ("Nirmala UI", 11)

        # ================= DATABASE =================
        self.conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )
        self.cursor = self.conn.cursor()

        self.member_dict = {}

        self.create_widgets()
        self.load_members()
        self.generate_subcode()
        self.load_treeview()

    # ================= UI =================
    def create_widgets(self):

        # ---------- HEADER ----------
        header = tk.Frame(self.frame, bg="#8df3cb", height=60)
        header.pack(fill="x")

        tk.Label(header,
                 text="उप-खाते नोंदणी",
                 bg="#8df3cb",
                 fg="blue",
                 font=("Segoe UI", 18, "bold")
                 ).pack(side="left", padx=20)

        tk.Button(header,
                  text="बाहेर पडा",
                  bg="#e74c3c",
                  fg="white",
                  command=self.frame.destroy
                  ).pack(side="right", padx=20, pady=10)

        # ---------- MAIN FRAME ----------
        main_frame = tk.Frame(self.frame, padx=20, pady=15, bg="#ecf0f1")
        main_frame.pack(fill="both", expand=True)

        # ---------- FORM ----------
        form_frame = tk.LabelFrame(
            main_frame,
            text="उप-खाते माहिती",
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=15,
            bg="#dff9fb"   # 👈 Background colour
            )
        form_frame.pack(fill="x", pady=10)

        tk.Label(form_frame, text="सदस्य निवडा",bg="#dff9fb",
                 font=self.marathi_font).grid(row=0, column=0, padx=10, pady=8)

        self.combo = ttk.Combobox(form_frame, width=25, state="readonly")
        self.combo.grid(row=0, column=1, padx=10, pady=8)
        self.combo.bind("<<ComboboxSelected>>", self.show_flat_no)

        tk.Label(form_frame, text="फ्लॅट क्रमांक",bg="#dff9fb",
                 font=self.marathi_font).grid(row=0, column=2, padx=10)

        #self.flat_label = tk.Label(form_frame, text="", fg="blue")
        self.flat_label = tk.Label(
            form_frame,
            text="",
            bg="#dff9fb",
            fg="blue",
            font=("Segoe UI", 18, "bold")   # 👈 Large Font
)
        self.flat_label.grid(row=0, column=3)

        tk.Label(form_frame, text="उप-खाते क्रमांक",bg="#dff9fb",
                 font=self.marathi_font).grid(row=1, column=0, padx=10, pady=8)

        self.subcode_entry = tk.Entry(form_frame, width=20, state="readonly")
        self.subcode_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(form_frame, text="उप-खाते नाव",bg="#dff9fb",
                 font=self.marathi_font).grid(row=1, column=2, padx=10)

        self.subname_entry = tk.Entry(form_frame, width=25)
        self.subname_entry.grid(row=1, column=3, padx=10)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(main_frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="जतन करा", width=12,
                  bg="#2ecc71", fg="white",
                  command=self.save_data).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="सुधारा", width=12,
                  bg="#3498db", fg="white",
                  command=self.update_data).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="काढून टाका", width=12,
                  bg="#e74c3c", fg="white",
                  command=self.delete_data).grid(row=0, column=2, padx=10)

        tk.Button(btn_frame, text="रिकामे करा", width=12,
                  bg="#95a5a6", fg="white",
                  command=self.clear_data).grid(row=0, column=3, padx=10)

        # ---------- SEARCH ----------
        search_frame = tk.Frame(main_frame, bg="#ecf0f1")
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="शोधा:",
                 font=("Segoe UI", 10, "bold"),
                 bg="#ecf0f1").pack(side="left", padx=5)

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(search_frame, text="शोध",
                  command=self.search_data).pack(side="left", padx=5)

        tk.Button(search_frame, text="सर्व दाखवा",
                  command=self.load_treeview).pack(side="left", padx=5)

        # ---------- TREEVIEW ----------
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Flat_No", "Member_Name", "Subac_code", "Subac_Name"),
            show="headings",
            yscrollcommand=scroll_y.set
        )

        self.tree.pack(fill="both", expand=True)
        scroll_y.config(command=self.tree.yview)

        self.tree.heading("Flat_No", text="फ्लॅट")
        self.tree.heading("Member_Name", text="सदस्य नाव")
        self.tree.heading("Subac_code", text="उप-खाते क्रमांक")
        self.tree.heading("Subac_Name", text="उप-खाते नाव")

        self.tree.column("Flat_No", width=80, anchor="center")
        self.tree.column("Member_Name", width=200)
        self.tree.column("Subac_code", width=120, anchor="center")
        self.tree.column("Subac_Name", width=200)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ================= DATABASE METHODS =================
    def load_members(self):
        self.cursor.execute("SELECT Flat_No, Member_Name FROM Member_Mast")
        rows = self.cursor.fetchall()

        names = []
        self.member_dict.clear()

        for row in rows:
            names.append(row.Member_Name)
            self.member_dict[row.Member_Name] = row.Flat_No

        self.combo['values'] = names

    def generate_subcode(self):
        self.cursor.execute("SELECT ISNULL(MAX(Subac_code),0) + 1 FROM SubMember_Mast")
        next_code = self.cursor.fetchone()[0]

        self.subcode_entry.config(state="normal")
        self.subcode_entry.delete(0, tk.END)
        self.subcode_entry.insert(0, str(next_code))
        self.subcode_entry.config(state="readonly")

    def show_flat_no(self, event=None):
        name = self.combo.get()
        self.flat_label.config(text=str(self.member_dict.get(name, "")))

    # ================= CRUD =================
    def save_data(self):
        if not self.combo.get() or not self.subname_entry.get():
            messagebox.showerror("त्रुटी", "सर्व माहिती भरणे आवश्यक आहे")
            return

        self.cursor.execute("""
            INSERT INTO SubMember_Mast
            (Flat_No, Member_Name, Subac_code, Subac_Name)
            VALUES (?, ?, ?, ?)
        """, (
            self.flat_label.cget("text"),
            self.combo.get(),
            self.subcode_entry.get(),
            self.subname_entry.get()
        ))

        self.conn.commit()
        messagebox.showinfo("यशस्वी", "नोंद जतन केली")
        self.clear_data()
        self.generate_subcode()
        self.load_treeview()

    def update_data(self):
        self.cursor.execute("""
            UPDATE SubMember_Mast
            SET Flat_No=?, Member_Name=?, Subac_Name=?
            WHERE Subac_code=?
        """, (
            self.flat_label.cget("text"),
            self.combo.get(),
            self.subname_entry.get(),
            self.subcode_entry.get()
        ))

        self.conn.commit()
        messagebox.showinfo("यशस्वी", "नोंद सुधारली")
        self.load_treeview()

    def delete_data(self):
        self.cursor.execute(
            "DELETE FROM SubMember_Mast WHERE Subac_code=?",
            (self.subcode_entry.get(),)
        )

        self.conn.commit()
        messagebox.showinfo("यशस्वी", "नोंद काढली")
        self.clear_data()
        self.generate_subcode()
        self.load_treeview()

    def clear_data(self):
        self.combo.set("")
        self.flat_label.config(text="")
        self.subname_entry.delete(0, tk.END)

    # ================= TREE =================
    def load_treeview(self):
        self.tree.delete(*self.tree.get_children())

        self.cursor.execute("""
        SELECT Flat_No, Member_Name, Subac_code, Subac_Name
        FROM SubMember_Mast
        ORDER BY Subac_code
        """)

        for row in self.cursor.fetchall():
            flat_no = f"{int(row[0]):03d}"
            self.tree.insert("", tk.END,
                             values=(flat_no, row[1], row[2], row[3]))

    def search_data(self):
        keyword = self.search_entry.get()

        if keyword == "":
            self.load_treeview()
            return

        self.tree.delete(*self.tree.get_children())

        self.cursor.execute("""
        SELECT Flat_No, Member_Name, Subac_code, Subac_Name
        FROM SubMember_Mast
        WHERE Member_Name LIKE ?
           OR Subac_Name LIKE ?
           OR CAST(Subac_code AS VARCHAR) LIKE ?
           OR CAST(Flat_No AS VARCHAR) LIKE ?
        ORDER BY Subac_code
        """, ('%' + keyword + '%',) * 4)

        for row in self.cursor.fetchall():
            flat_no = f"{int(row[0]):03d}"
            self.tree.insert("", tk.END,
                             values=(flat_no, row[1], row[2], row[3]))

    def on_tree_select(self, event=None):
        selected = self.tree.focus()
        values = self.tree.item(selected, "values")

        if values:
            self.flat_label.config(text=values[0])
            self.combo.set(values[1])

            self.subcode_entry.config(state="normal")
            self.subcode_entry.delete(0, tk.END)
            self.subcode_entry.insert(0, values[2])
            self.subcode_entry.config(state="readonly")

            self.subname_entry.delete(0, tk.END)
            self.subname_entry.insert(0, values[3])