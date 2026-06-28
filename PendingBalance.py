import pyodbc
import pandas as pd
import tkinter as tk
from tkinter import ttk

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
def connect_db():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=SARTHAK;"
        "DATABASE=socity_db;"
        "Trusted_Connection=yes;"
    )


# -----------------------------------
# CALCULATE CURRENT MONTH PENDING
# -----------------------------------
def calculate_pending():

    conn = connect_db()

    member = pd.read_sql("""
        SELECT Flat_No, Member_Name
        FROM Member_Mast
    """, conn)

    maintenance = pd.read_sql("""
        SELECT Flat_No, Yearly_Amount
        FROM Yearly_Flat_Maintenance
    """, conn)

    opening = pd.read_sql("""
        SELECT Flat_No,
               SUM(ISNULL(Debit,0))  AS Opening_Debit,
               SUM(ISNULL(Credit,0)) AS Opening_Credit
        FROM Opening_Balance
        GROUP BY Flat_No
    """, conn)

    payment = pd.read_sql("""
        SELECT Flat_No,
               SUM(ISNULL(Credit,0)) AS Paid
        FROM Dailytrans1
        GROUP BY Flat_No
    """, conn)

    conn.close()

    # Merge tables
    df = member.merge(maintenance, on="Flat_No", how="left")
    df = df.merge(opening, on="Flat_No", how="left")
    df = df.merge(payment, on="Flat_No", how="left")

    df = df.fillna(0)

    # -----------------------------------
    # CALCULATIONS
    # -----------------------------------

    df["Opening_Pending"] = df["Opening_Debit"] - df["Opening_Credit"]

    df["Monthly_Maintenance"] = df["Yearly_Amount"] / 12

    df["Current_Month_Due"] = df["Opening_Pending"] + df["Monthly_Maintenance"]

    df["Current_Pending"] = df["Current_Month_Due"] - df["Paid"]

    return df


# -----------------------------------
# LOAD DATA INTO GUI TABLE
# -----------------------------------
def load_report():

    df = calculate_pending()

    for row in tree.get_children():
        tree.delete(row)

    for _, r in df.iterrows():

        tree.insert("", "end", values=(
            r["Flat_No"],
            r["Member_Name"],
            round(r["Opening_Pending"],2),
            round(r["Monthly_Maintenance"],2),
            round(r["Paid"],2),
            round(r["Current_Pending"],2)
        ))


# -----------------------------------
# GUI DESIGN
# -----------------------------------
root = tk.Tk()
root.title("Society Current Month Pending Report")
root.geometry("900x500")

title = tk.Label(root,
                 text="Current Month Maintenance Pending",
                 font=("Arial",16,"bold"))
title.pack(pady=10)

columns = (
    "Flat",
    "Member",
    "Opening Pending",
    "Monthly Maintenance",
    "Paid",
    "Current Pending"
)

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)

tree.pack(fill="both", expand=True)

btn = tk.Button(root,
                text="Generate Report",
                command=load_report,
                bg="green",
                fg="white",
                font=("Arial",12))

btn.pack(pady=10)

root.mainloop()