import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc


class YearlyMaintenanceEntry(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Yearly Maintenance Entry")
        self.geometry("500x300")
        self.resizable(False, False)

        self.create_widgets()
        self.load_flats()

    # ================= DATABASE CONNECTION =================
    def get_connection(self):
        return pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=Sarthak;"
            "DATABASE=Socity_db;"
            "Trusted_Connection=yes;"
        )

    # ================= UI DESIGN =================
    def create_widgets(self):

        main_frame = tk.LabelFrame(self, text="Enter Yearly Maintenance", padx=20, pady=20)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Flat No
        tk.Label(main_frame, text="Flat No").grid(row=0, column=0, pady=10, sticky="w")
        self.flat_combo = ttk.Combobox(main_frame, width=25)
        self.flat_combo.grid(row=0, column=1, pady=10)

        # Year
        tk.Label(main_frame, text="Year").grid(row=1, column=0, pady=10, sticky="w")
        from datetime import datetime

        tk.Label(main_frame, text="Year").grid(row=1, column=0, pady=10, sticky="w")

        self.year_combo = ttk.Combobox(main_frame, width=25, state="readonly")
        self.year_combo.grid(row=1, column=1, pady=10)

# Generate year list (2020 to 2035)
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 10))

        self.year_combo["values"] = years
        self.year_combo.set(current_year)   # default current year

        # Yearly Amount
        tk.Label(main_frame, text="Yearly Amount").grid(row=2, column=0, pady=10, sticky="w")
        self.amount_entry = tk.Entry(main_frame, width=28)
        self.amount_entry.grid(row=2, column=1, pady=10)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Save", width=10,
                  command=self.save_record).grid(row=0, column=0, padx=5)

        tk.Button(button_frame, text="Update", width=10,
                  command=self.update_record).grid(row=0, column=1, padx=5)

        tk.Button(button_frame, text="Exit", width=10,
                  bg="red", fg="white",
                  command=self.destroy).grid(row=0, column=2, padx=5)

    # ================= LOAD FLAT NUMBERS =================
    def load_flats(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Flat_No FROM Member_Mast ORDER BY Flat_No")
            flats = [str(row[0]) for row in cursor.fetchall()]
            conn.close()

            self.flat_combo["values"] = flats
            if flats:
                self.flat_combo.current(0)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ================= SAVE =================
    def save_record(self):
        flat_no = self.flat_combo.get()
        year = self.year_combo.get()
        amount = self.amount_entry.get()

        if not flat_no or not year or not amount:
            messagebox.showwarning("Warning", "All fields are required")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check duplicate
            cursor.execute("""
                SELECT * FROM Yearly_Flat_Maintenance
                WHERE Flat_No=? AND Year=?
            """, flat_no, year)

            if cursor.fetchone():
                messagebox.showwarning("Warning", "Record already exists")
                conn.close()
                return

            cursor.execute("""
                INSERT INTO Yearly_Flat_Maintenance
                (Flat_No, Year, Yearly_Amount)
                VALUES (?, ?, ?)
            """, flat_no, year, amount)

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Record Saved Successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= UPDATE =================
    def update_record(self):
        flat_no = self.flat_combo.get()
        year = self.year_entry.get()
        amount = self.amount_entry.get()

        if not flat_no or not year or not amount:
            messagebox.showwarning("Warning", "All fields are required")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Yearly_Flat_Maintenance
                SET Yearly_Amount=?
                WHERE Flat_No=? AND Year=?
            """, amount, flat_no, year)

            if cursor.rowcount == 0:
                messagebox.showwarning("Warning", "Record Not Found")
            else:
                messagebox.showinfo("Success", "Record Updated")

            conn.commit()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


# ================= RUN DIRECTLY =================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    YearlyMaintenanceEntry(root)
    root.mainloop()