#import cx_Oracle
import tkinter as tk
from tkinter import messagebox
import pyodbc
from tkinter import ttk

# ---------- Oracle Connection ----------
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=Tractor-2;"
        "DATABASE=Sai_db;"
        "Trusted_Connection=yes;"
    )

# ---------- CRUD Functions ----------
#------------ADD RECORD TO DATABASE TABLE -----------------
def add_record():
    try:
        con = get_connection()
        cur = con.cursor()

        # 🔍 Check duplicate plot_no
        cur.execute(
            "SELECT COUNT(*) FROM plot_master WHERE plot_no = ?",
            (plot_no.get(),)
        )
        count = cur.fetchone()[0]

        if count > 0:
            messagebox.showwarning(
                "Duplicate Record",
                f"Plot No {plot_no.get()} already exists!"
            )
            return

        # ✅ Insert if not duplicate
        cur.execute("""
            INSERT INTO plot_master
            (plot_no, owner_name, address, mobile1, mobile2, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        plot_no.get(),
        owner_name.get(),
        address.get(),
        mobile1.get(),
        mobile2.get(),
        email.get()
        )

        con.commit()
        load_grid()
        messagebox.showinfo("Success", "Record Added")

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        con.close()

#------------GET RECORD FROM TABLE -----------------
def get_record():
    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute(
            "SELECT plot_no, owner_name, address, mobile1, mobile2, email "
            "FROM plot_master WHERE plot_no = ?",
            (plot_no.get(),)
        )

        row = cur.fetchone()

        if row:
            owner_name.set(row[1])
            address.set(row[2])
            mobile1.set(row[3])
            mobile2.set(row[4])
            email.set(row[5])
        else:
            messagebox.showinfo("Info", "Record not found")

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        con.close()
#------------UPDATE RECORD TO TABLE -----------------
def update_record():
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            UPDATE plot_master SET
                owner_name = ?,
                address    = ?,
                mobile1    = ?,
                mobile2    = ?,
                email      = ?
            WHERE plot_no = ?
        """,
        owner_name.get(),
        address.get(),
        mobile1.get(),
        mobile2.get(),
        email.get(),
        plot_no.get()
        )
        con.commit()
        load_grid()
        messagebox.showinfo("Success", "Record Updated")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()
#------------DELETE RECORD TO TABLE -----------------
def delete_record():
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM plot_master WHERE plot_no = ?",
            (plot_no.get(),)
        )
        con.commit()
        load_grid()
        clear_fields()
        messagebox.showinfo("Success", "Record Deleted")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()
#------------CLEAR FIELD  -----------------
def clear_fields():
    plot_no.set("")
    owner_name.set("")
    address.set("")
    mobile1.set("")
    mobile2.set("")
    email.set("")

# ---------- GUI ----------
root = tk.Tk()
root.title("Plot Master")
root.configure(bg="#c9eff2")
plot_no = tk.StringVar()
owner_name = tk.StringVar()
address = tk.StringVar()
mobile1 = tk.StringVar()
mobile2 = tk.StringVar()
email = tk.StringVar()

labels = [
    "प्लॉट नंबर",
    "प्लॉट धारकाचे नाव",
    "प्लॉट धारकाचा पत्ता",
    "मोबाईल नंबर - 1",
    "मोबाईल नंबर - 2",
    "ईमेल"
]

vars = [plot_no, owner_name, address, mobile1, mobile2, email]

for i, text in enumerate(labels):
    tk.Label(root, text=text, font=("Arial", 15)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
    tk.Entry(root, textvariable=vars[i], width=40).grid(row=i, column=1, pady=5)

#tk.Button(root, text="Get", width=10, command=get_record).grid(row=0, column=2, padx=10)

#tk.Button(root, text="Add", width=10, command=add_record).grid(row=7, column=0)
#tk.Button(root, text="Update", width=10, command=update_record).grid(row=7, column=1)
#tk.Button(root, text="Delete", width=10, command=delete_record).grid(row=7, column=2)
#tk.Button(root, text="Exit", width=10, command=root.quit).grid(row=7, column=3)
#---------BUTTON FRAME---------------
#button_frame = tk.Frame(root)
button_frame = tk.Frame(root, bd=5,pady=15, relief="ridge")

button_frame.grid(row=7, column=0, columnspan=4, pady=10)

tk.Button(button_frame, text="Add", width=10,bg="lightblue", command=add_record)\
    .grid(row=0, column=0, padx=15)

tk.Button(button_frame, text="Update", width=10,bg="lightblue", command=update_record)\
    .grid(row=0, column=1, padx=15)

tk.Button(button_frame, text="Delete", width=10,bg="lightblue", command=delete_record)\
    .grid(row=0, column=2, padx=15)

tk.Button(button_frame, text="Exit", width=10,bg="orange", command=root.quit)\
    .grid(row=0, column=3, padx=15)

   
# ---------- Search ----------
search_frame = tk.Frame(root, bd=2, relief="groove")
search_frame.grid(row=8, column=0, columnspan=4, pady=10, padx=10, sticky="w")

search_var = tk.StringVar()

tk.Label(search_frame,
         text="Search",
         font=("Arial", 10, "bold")
         ).grid(row=0, column=0, padx=5, pady=5)

search_entry = tk.Entry(search_frame,
                        textvariable=search_var,
                        width=30)
search_entry.grid(row=0, column=1, padx=5, pady=5)

search_var.trace_add("write", lambda *args: load_grid())

# ---------- TREEVIEW FRAME ----------
#tree_frame = tk.Frame(root)
#tree_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
tree_frame = tk.Frame(root)
tree_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

tree_frame = tk.Frame(root)
tree_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

columns = ("plot_no", "owner_name", "address", "mobile1", "mobile2", "email")

tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    height=5
)

# Headings
tree.heading("plot_no", text="प्लॉट नं.")
tree.heading("owner_name", text="मालकाचे नाव")
tree.heading("address", text="पत्ता")
tree.heading("mobile1", text="मोबाईल १")
tree.heading("mobile2", text="मोबाईल २")
tree.heading("email", text="ईमेल")

# Columns
tree.column("plot_no", width=80, anchor="center")
tree.column("owner_name", width=160)
tree.column("address", width=220)
tree.column("mobile1", width=120, anchor="center")
tree.column("mobile2", width=120, anchor="center")
tree.column("email", width=180)

# Scrollbars
scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

tree.configure(
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

# Pack ONLY (inside frame)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

#-----CONFIGURE HIGHLIGHT TAG----------------
tree.tag_configure("highlight", background="#ecd60d")  # light yellow


#------------DISPLAY GRID OR LOAD GRID -----------------
def load_grid():
    for item in tree.get_children():
        tree.delete(item)

    try:
        con = get_connection()
        cur = con.cursor()

        search_text = search_var.get().lower()

        # Always load ALL records
        cur.execute("""
            SELECT plot_no, owner_name, address, mobile1, mobile2, email
            FROM plot_master
            ORDER BY plot_no
        """)

        for row in cur.fetchall():
            values = tuple(row)

            # Check if search text matches any column
            if search_text and any(search_text in str(value).lower() for value in values):
                tree.insert("", tk.END, values=values, tags=("highlight",))
            else:
                tree.insert("", tk.END, values=values)

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        con.close()


#-----SEARCH CLEAR BUTTON ----------
    clear_btn = tk.Button(
    root,
    text="❌ Clear",
    width=8,
    command=clear_search
)
    clear_btn.grid(row=8, column=1, padx=5)

#------------ON ROW SELECT -----------------
def on_row_select(event):
    selected_item = tree.focus()
    if not selected_item:
        return

    values = tree.item(selected_item, "values")

    plot_no.set(values[0])
    owner_name.set(values[1])
    address.set(values[2])
    mobile1.set(values[3])
    mobile2.set(values[4])
    email.set(values[5])

tree.bind("<<TreeviewSelect>>", on_row_select)
##------------SEARCH CLEAR BUTTON-----------------
def clear_search():
    search_var.set("")   # clear search box
    load_grid()          # reload full grid

#-------ADD VERTICAL SCROLL BAR--------

scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)

scroll_y.pack(side="right", fill="y")

# Load data ON START
load_grid()

root.mainloop()

