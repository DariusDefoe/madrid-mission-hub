#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime
from urllib.parse import urlparse
import os

# Parse MySQL Connection Details
mysql_conn = os.environ.get("MYSQL_CONNECTION")
if mysql_conn:
    url = urlparse(mysql_conn)
    db_config = {
        "host": url.hostname,
        "user": url.username,
        "password": url.password,
        "database": url.path.lstrip('/'),
        "port": url.port if url.port else 3306
    }
else:
    db_config = {
        "host": os.environ.get("DB_HOST"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "database": os.environ.get("DB_NAME")
    }

# Autocomplete Combobox
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._handle_keyrelease)
    def _handle_keyrelease(self, event):
        if event.keysym in ("BackSpace", "Left", "Right", "Up", "Down", "Return", "Escape"):
            return
        value = self.get().lower()
        matches = [item for item in self._completion_list if item.lower().startswith(value)]
        self['values'] = matches if matches else self._completion_list
        if matches:
            self.event_generate('<Down>')

# Database Fetch Functions
def fetch_data_from_db():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT Supplier_ID, Supplier_Name FROM NIF_Codes")
        return cur.fetchall()
    except Error:
        return []
    finally:
        if conn and conn.is_connected():
            cur.close(); conn.close()

def fetch_budget_heads():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT Head_of_Accounts_ID, Head_of_Accounts_Name FROM Head_of_Accounts")
        rows = cur.fetchall()
        return {name: head_id for head_id, name in rows}
    except Error:
        return {}
    finally:
        if conn and conn.is_connected():
            cur.close(); conn.close()

# Main Transaction Function
def submit_transaction():
    supplier = supplier_var.get().strip()
    inv_num = invoice_number_entry.get().strip()
    inv_date = invoice_date_entry.get().strip()
    inv_amt = invoice_amount_var.get().strip()
    inv_vat = invoice_vat_var.get().strip()
    refundable = vat_refundable_var.get()
    status = status_var.get().strip()
    if not all([supplier, inv_num, inv_date, inv_amt, status]):
        status_label.config(text="Fill all required fields.", fg="red"); return
    try:
        inv_amt = float(inv_amt)
        inv_vat = float(inv_vat) if inv_vat else 0.0
        datetime.strptime(inv_date, '%Y-%m-%d')
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red"); return
    supp_id = supplier_id_map.get(supplier)
    if not supp_id:
        status_label.config(text="Invalid supplier.", fg="red"); return
    voucher_id = None
    voucher = entry_voucher_number.get().strip()
    if voucher:
        voucher = voucher.zfill(10)
        benef = entry_voucher_beneficiary.get().strip()
        vou_euro = entry_voucher_euro.get().strip()
        vou_quarter = entry_voucher_quarter.get().strip()
        vou_year = entry_voucher_year.get().strip()
        bud_head = budget_head_var.get().strip()
        if not all([voucher, benef, vou_euro, vou_quarter, vou_year, bud_head]):
            status_label.config(text="Fill all voucher fields.", fg="red"); return
        try:
            vou_euro = float(vou_euro)
            vou_quarter = int(vou_quarter)
            vou_year = int(vou_year)
        except:
            status_label.config(text="Voucher numeric fields error.", fg="red"); return
        head_id = budget_heads.get(bud_head)
        if not head_id:
            status_label.config(text="Invalid budget head.", fg="red"); return
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Invoices_Residence WHERE Number = %s", (inv_num,))
        if cur.fetchone():
            status_label.config(text="Duplicate invoice.", fg="red"); return
        if voucher:
            cur.execute(
                """INSERT INTO Vouchers (Voucher_Number, Head_of_Accounts_ID, Voucher_Beneficiary,
                Voucher_Euro, Voucher_Quarter, Voucher_Year) VALUES (%s, %s, %s, %s, %s, %s)""",
                (voucher, head_id, benef, vou_euro, vou_quarter, vou_year)
            )
            voucher_id = cur.lastrowid
            cur.execute(
                """INSERT INTO Invoices_Residence (Supplier_ID, Number, Date, Total, Vat, Refundable, Status, Voucher_ID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (supp_id, inv_num, inv_date, inv_amt, inv_vat, refundable, status, voucher_id)
            )
        else:
            cur.execute(
                """INSERT INTO Invoices_Residence (Supplier_ID, Number, Date, Total, Vat, Refundable, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (supp_id, inv_num, inv_date, inv_amt, inv_vat, refundable, status)
            )
        conn.commit()
        msg = f"Invoice ID: {cur.lastrowid}"
        if voucher_id: msg += f", Voucher ID: {voucher_id}"
        status_label.config(text=msg, fg="green")
        clear_form()
    except Error as e:
        status_label.config(text=f"DB Error: {e}", fg="red")
    finally:
        if conn and conn.is_connected():
            cur.close(); conn.close()

def clear_form():
    supplier_var.set('')
    invoice_number_entry.delete(0, tk.END)
    invoice_date_entry.delete(0, tk.END)
    invoice_amount_var.set('')
    invoice_vat_var.set('')
    vat_refundable_var.set(0)
    status_var.set('')
    calculate_vat_var.set(0)
    entry_voucher_number.delete(0, tk.END)
    entry_voucher_beneficiary.delete(0, tk.END)
    entry_voucher_euro.delete(0, tk.END)
    entry_voucher_quarter.delete(0, tk.END)
    entry_voucher_year.delete(0, tk.END)
    budget_head_var.set('')

def calculate_vat(*args):
    if calculate_vat_var.get():
        try:
            total = float(invoice_amount_var.get())
            vat = round(total * 0.21 / 1.21, 2)
            invoice_vat_var.set(str(vat))
            invoice_vat_entry.config(state='readonly')
        except:
            invoice_vat_var.set('')
    else:
        invoice_vat_var.set('')
        invoice_vat_entry.config(state='normal')

def batch_insert():
    path = filedialog.askopenfilename(initialdir="/home/user/INVOICES/", title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    if not path: return
    invoices, errors = [], []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            req = ["Supplier_Name", "Invoice_Number", "Invoice_Date", "Invoice_Amount", "Invoice_VAT", "Refundable"]
            for field in req:
                if field not in reader.fieldnames:
                    messagebox.showerror("CSV Error", f"Missing field: {field}")
                    return
            has_status = "Status" in reader.fieldnames
            for i, row in enumerate(reader, start=2):
                try:
                    supp = row["Supplier_Name"].strip()
                    invn = row["Invoice_Number"].strip()
                    invd = row["Invoice_Date"].strip()
                    amt = float(row["Invoice_Amount"].strip())
                    vat = float(row["Invoice_VAT"].strip())
                    ref = int(row["Refundable"].strip())
                    stat = row["Status"].strip() if has_status and row["Status"].strip() else "Pending"
                    datetime.strptime(invd, '%Y-%m-%d')
                    sid = supplier_id_map.get(supp)
                    if not sid: raise ValueError(f"Supplier '{supp}' not found.")
                    invoices.append((sid, invn, invd, amt, vat, ref, stat))
                except Exception as e:
                    errors.append(f"Line {i}: {e}")
    except Exception as e:
        messagebox.showerror("File Error", f"{e}")
        return
    if errors:
        messagebox.showerror("CSV Errors", "\n".join(errors))
    if not invoices:
        messagebox.showinfo("Batch Insert", "No valid invoices.")
        return
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        nums = [inv[1] for inv in invoices]
        fmt = ','.join(['%s'] * len(nums))
        cur.execute(f"SELECT Number FROM Invoices_Residence WHERE Number IN ({fmt})", tuple(nums))
        existing = {r[0] for r in cur.fetchall()}
        unique = [inv for inv in invoices if inv[1] not in existing]
        if not unique:
            messagebox.showinfo("Batch Insert", "No new invoices.")
            return
        cur.executemany(
            """INSERT INTO Invoices_Residence (Supplier_ID, Number, Date, Total, Vat, Refundable, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", unique
        )
        conn.commit()
        status_label.config(text=f"Inserted {cur.rowcount} invoices.", fg="green")
    except Error as e:
        status_label.config(text=f"DB Error: {e}", fg="red")
    finally:
        if conn and conn.is_connected():
            cur.close(); conn.close()

# GUI Setup
root = tk.Tk()
root.title("Residence Invoice Entry Form")
root.geometry("1100x700")
lbl_font = ("Helvetica", 14)
btn_font = ("Helvetica", 14)
w = 50

tk.Label(root, text="Supplier:", font=lbl_font).grid(row=0, column=0, padx=20, pady=15, sticky="e")
supplier_var = tk.StringVar()
supplier_dropdown = AutocompleteCombobox(root, textvariable=supplier_var, font=lbl_font, width=w-10)
supplier_dropdown.set_completion_list([s[1] for s in fetch_data_from_db()])
supplier_dropdown.grid(row=0, column=1, padx=20, pady=15)

tk.Label(root, text="Invoice Number:", font=lbl_font).grid(row=1, column=0, padx=20, pady=15, sticky="e")
invoice_number_entry = tk.Entry(root, font=lbl_font, width=w)
invoice_number_entry.grid(row=1, column=1, padx=20, pady=15)

tk.Label(root, text="Invoice Date (YYYY-MM-DD):", font=lbl_font).grid(row=2, column=0, padx=20, pady=15, sticky="e")
invoice_date_entry = tk.Entry(root, font=lbl_font, width=w)
invoice_date_entry.grid(row=2, column=1, padx=20, pady=15)

tk.Label(root, text="Invoice Amount:", font=lbl_font).grid(row=3, column=0, padx=20, pady=15, sticky="e")
invoice_amount_var = tk.StringVar()
invoice_amount_entry = tk.Entry(root, textvariable=invoice_amount_var, font=lbl_font, width=w)
invoice_amount_entry.grid(row=3, column=1, padx=20, pady=15)
calculate_vat_var = tk.IntVar()
tk.Checkbutton(root, text="Calculate VAT at 21%", variable=calculate_vat_var, font=lbl_font, command=calculate_vat)\
    .grid(row=3, column=2, padx=20, pady=15, sticky="w")
invoice_amount_var.trace_add('write', calculate_vat)

tk.Label(root, text="Invoice VAT:", font=lbl_font).grid(row=4, column=0, padx=20, pady=15, sticky="e")
invoice_vat_var = tk.StringVar()
invoice_vat_entry = tk.Entry(root, textvariable=invoice_vat_var, font=lbl_font, width=w)
invoice_vat_entry.grid(row=4, column=1, padx=20, pady=15)

tk.Label(root, text="VAT Refundable:", font=lbl_font).grid(row=5, column=0, padx=20, pady=15, sticky="e")
vat_refundable_var = tk.IntVar()
tk.Checkbutton(root, variable=vat_refundable_var, font=lbl_font)\
    .grid(row=5, column=1, padx=20, pady=15, sticky="w")

tk.Label(root, text="Status:", font=lbl_font).grid(row=6, column=0, padx=20, pady=15, sticky="e")
status_var = tk.StringVar()
status_dropdown = ttk.Combobox(root, textvariable=status_var, font=lbl_font, width=w-10)
status_dropdown['values'] = ["Pending", "Processed", "Archived"]
status_dropdown.grid(row=6, column=1, padx=20, pady=15)

# Voucher Section
sep = ttk.Separator(root, orient='horizontal')
sep.grid(row=7, column=0, columnspan=3, sticky="ew", padx=20, pady=20)
tk.Label(root, text="Voucher Entry (Optional):", font=("Helvetica", 16, "bold"))\
    .grid(row=8, column=0, columnspan=3, padx=20, pady=10)
tk.Label(root, text="Voucher Number:", font=lbl_font).grid(row=9, column=0, padx=20, pady=10, sticky="e")
entry_voucher_number = tk.Entry(root, font=lbl_font, width=w)
entry_voucher_number.grid(row=9, column=1, padx=20, pady=10, sticky="w")
tk.Label(root, text="Voucher Beneficiary:", font=lbl_font).grid(row=10, column=0, padx=20, pady=10, sticky="e")
entry_voucher_beneficiary = tk.Entry(root, font=lbl_font, width=w)
entry_voucher_beneficiary.grid(row=10, column=1, padx=20, pady=10, sticky="w")
tk.Label(root, text="Voucher Euro (€):", font=lbl_font).grid(row=11, column=0, padx=20, pady=10, sticky="e")
entry_voucher_euro = tk.Entry(root, font=lbl_font, width=w)
entry_voucher_euro.grid(row=11, column=1, padx=20, pady=10, sticky="w")
tk.Label(root, text="Voucher Quarter:", font=lbl_font).grid(row=12, column=0, padx=20, pady=10, sticky="e")
entry_voucher_quarter = tk.Entry(root, font=lbl_font, width=w)
entry_voucher_quarter.grid(row=12, column=1, padx=20, pady=10, sticky="w")
tk.Label(root, text="Voucher Year:", font=lbl_font).grid(row=13, column=0, padx=20, pady=10, sticky="e")
entry_voucher_year = tk.Entry(root, font=lbl_font, width=w)
entry_voucher_year.grid(row=13, column=1, padx=20, pady=10, sticky="w")
tk.Label(root, text="Budget Head:", font=lbl_font).grid(row=14, column=0, padx=20, pady=10, sticky="e")
budget_head_var = tk.StringVar()
budget_heads = fetch_budget_heads()
if budget_heads:
    budget_head_var.set(list(budget_heads.keys())[0])
option_menu = tk.OptionMenu(root, budget_head_var, *budget_heads.keys())
option_menu.config(font=lbl_font)
option_menu.grid(row=14, column=1, padx=20, pady=10, sticky="w")


submit_button = tk.Button(root, text="Submit", command=submit_transaction, font=btn_font, width=20)
submit_button.grid(row=15, column=1, padx=20, pady=20, sticky="w")
batch_insert_button = tk.Button(root, text="Batch Insert", command=batch_insert, font=btn_font, width=20, bg="#4CAF50", fg="white")
batch_insert_button.grid(row=15, column=2, padx=20, pady=20, sticky="w")
status_label = tk.Label(root, text="", font=lbl_font)
status_label.grid(row=16, column=0, columnspan=3, padx=20, pady=15)

supplier_data = fetch_data_from_db()
supplier_id_map = {s[1]: s[0] for s in supplier_data}

root.mainloop()
