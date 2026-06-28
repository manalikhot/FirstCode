import tkinter as tk
from tkinter import messagebox
#import oracledb
import pyodbc
from tkinter import ttk


# ------------------ DATABASE CONNECTION ------------------ #

def connect_db():
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Sai_db;"
            "Trusted_Connection=yes;"
        )
        return connection   # ✅ IMPORTANT
    except Exception as e:
        print("Database Error:", e)
        return None


# ------------------ CREATE RECORD ------------------ #
def insert_member(): #This defines a function named insert_member.
    conn = connect_db() #Calls the connect_db() function to connect to the database.

    if conn is None:
        messagebox.showerror("Error", "Database connection failed")
        return #Stops the function immediately.
    
    #Creates a cursor object.*Execute SQL querie,*Insert / Update / Delete data,*Fetch data
    #cursor=conn.cursor() is "SQL command executor".
    cursor = conn.cursor() 

    cursor.execute("""
        INSERT INTO Member_Mast
        (Flat_No, Member_Name, Member_Add, Member_Mob1, Member_Mob2, Member_Email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        flat_no.get(), # .get() → Retrieves the value typed in the textbox.
        name.get(),
        address.get(),
        mob1.get(),
        mob2.get(),
        email.get()
    ))

    conn.commit() # Use for Saves the changes permanently in the database.
    conn.close()

    messagebox.showinfo("Success", "Record Inserted Successfully")


# ------------------ READ RECORD ------------------ #
def fetch_member():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Member_Mast WHERE Flat_No = ?",(flat_no.get(),))

        #cursor.execute("SELECT * FROM Member_Mast WHERE Flat_No=:1", (flat_no.get(),)) #Oracl Query
        row = cursor.fetchone()

        if row:
            name.set(row[1])
            address.set(row[2])
            mob1.set(row[3])
            mob2.set(row[4])
            email.set(row[5])
        else:
            messagebox.showinfo("Info", "No Record Found")

        conn.close()
        load_data()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------ UPDATE RECORD ------------------ #
def update_member():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
    UPDATE Member_Mast
    SET Member_Name = ?,
        Member_Add = ?,
        Member_Mob1 = ?,
        Member_Mob2 = ?,
        Member_Email = ?
    WHERE Flat_No = ?
    """, (
    name.get(),
    address.get(),
    mob1.get(),
    mob2.get(),
    email.get(),
    flat_no.get()
    ))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Record Updated Successfully")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------ DELETE RECORD ------------------ #
def delete_member():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #cursor.execute("DELETE FROM Member_Mast WHERE Flat_No=:1", (flat_no.get(),))
        cursor.execute("DELETE FROM Member_Mast WHERE Flat_No = ?", (flat_no.get(),))
        
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Record Deleted Successfully")

    except Exception as e:
        messagebox.showerror("Error", str(e))

#------Tree View Load Data ----------------
def load_data():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Flat_No, Member_Name, Member_Add,
               Member_Mob1, Member_Mob2, Member_Email
        FROM Member_Mast
    """)

    rows = cursor.fetchall()

    # Clear tree
    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        tree.insert("", "end", values=tuple(row))

    conn.close()

def exit_app():
    if messagebox.askyesno("Exit", "Do you want to exit?"):
        root.destroy()



# ------------------ GUI DESIGN ------------------ #
#import tkinter as tk

root = tk.Tk()
root.title("Member Management System")
#root.geometry("450x350")
root.geometry("600x550")

# Make columns responsive
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)

# Variables
flat_no = tk.IntVar()
name = tk.StringVar()
address = tk.StringVar()
mob1 = tk.StringVar()
mob2 = tk.StringVar()
email = tk.StringVar()

# Labels & Entries
tk.Label(root, text="Flat No").grid(row=0, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=flat_no, width=30).grid(row=0, column=1, padx=10, pady=8)

tk.Label(root, text="Member Name").grid(row=1, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=name, width=30).grid(row=1, column=1, padx=10, pady=8)

tk.Label(root, text="Address").grid(row=2, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=address, width=30).grid(row=2, column=1, padx=10, pady=8)

tk.Label(root, text="Mobile 1").grid(row=3, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=mob1, width=30).grid(row=3, column=1, padx=10, pady=8)

tk.Label(root, text="Mobile 2").grid(row=4, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=mob2, width=30).grid(row=4, column=1, padx=10, pady=8)

tk.Label(root, text="Email").grid(row=5, column=0, padx=10, pady=8, sticky="w")
tk.Entry(root, textvariable=email, width=30).grid(row=5, column=1, padx=10, pady=8)

# ---------------- BUTTON FRAME ---------------- #
button_frame = tk.Frame(root)
button_frame.grid(row=6, column=0, columnspan=4, pady=15)

# Make equal spacing
button_frame.columnconfigure((0,1,2,3,4), weight=1) #Make columns 0, 1, 2, and 3 expand equally when the window resizes.”
# weight=1 means This controls how extra space is distributed.
# Buttons Row

btn_insert = tk.Button(button_frame, text="Insert", width=12, command=insert_member)
btn_insert.grid(row=0, column=0, padx=15)

btn_update = tk.Button(button_frame, text="Update", width=12, command=update_member)
btn_update.grid(row=0, column=1, padx=15)

btn_fetch = tk.Button(button_frame, text="Fetch", width=12, command=fetch_member)
btn_fetch.grid(row=0, column=2, padx=15)

btn_delete = tk.Button(button_frame, text="Delete", width=12, command=delete_member)
btn_delete.grid(row=0, column=3, padx=15)

btn_delete = tk.Button(button_frame, text="Exit", width=12, command=exit_app)
btn_delete.grid(row=0, column=3, padx=15)

# Buttons Row
#tk.Button(root, text="Insert", width=10,command=insert_member).grid(row=6, column=0, pady=15)
#tk.Button(root, text="Update", width=10,command=update_member).grid(row=6,column=1,pady=15)
#tk.Button(root, text="Fetch", width=10,command=fetch_member).grid(row=6, column=2,pady=15)
#tk.Button(root, text="Delete", width=10,command=delete_member).grid(row=6,column=3,pady=15)

#---------Create Tree View -------------------
# Make window bigger
tree = ttk.Treeview(root)

tree["columns"] = ("Flat_No", "Member_Name", "Member_Add",
                   "Member_Mob1", "Member_Mob2", "Member_Email")

tree.column("#0", width=0, stretch=tk.NO)

tree.column("Flat_No", width=80, anchor=tk.CENTER)
tree.column("Member_Name", width=120, anchor=tk.W)
tree.column("Member_Add", width=150, anchor=tk.W)
tree.column("Member_Mob1", width=100, anchor=tk.CENTER)
tree.column("Member_Mob2", width=100, anchor=tk.CENTER)
tree.column("Member_Email", width=150, anchor=tk.W)

tree.heading("#0", text="")
tree.heading("Flat_No", text="Flat No")
tree.heading("Member_Name", text="Name")
tree.heading("Member_Add", text="Address")
tree.heading("Member_Mob1", text="Mobile 1")
tree.heading("Member_Mob2", text="Mobile 2")
tree.heading("Member_Email", text="Email")

tree.grid(row=7, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)


# Scrollbar
# Vertical Scrollbar
v_scrollbar = tk.Scrollbar(root, orient="vertical", command=tree.yview)
v_scrollbar.grid(row=7, column=4, sticky="ns")

# Horizontal Scrollbar
h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=tree.xview)
h_scrollbar.grid(row=8, column=0, columnspan=4, sticky="ew")

# Connect scrollbars to tree
tree.configure(yscrollcommand=v_scrollbar.set,
               xscrollcommand=h_scrollbar.set)


# Make tree expandable
root.grid_rowconfigure(7, weight=1)
root.grid_columnconfigure(1, weight=1)

# Load data initially

load_data()
root.mainloop()
