
#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox

# Database connection details
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "r0n4nd3giMik0n4d!",
    "database": "administration"
}

# Connect to the database using provided credentials
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL database successfully.")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to add supplier to the database and retrieve the new Supplier_ID
def add_supplier(connection, nif_code, supplier_name):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO administration.NIF_Codes (Supplier_NIF_Code, Supplier_Name)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (nif_code, supplier_name))
        connection.commit()
        
        # Retrieve the last inserted Supplier_ID
        new_supplier_id = cursor.lastrowid
        messagebox.showinfo("Success", f"Supplier added successfully with ID: {new_supplier_id}")
    except Error as e:
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        cursor.close()

# Function to handle button click event
def submit():
    nif_code = entry_nif.get()
    supplier_name = entry_name.get()

    if nif_code and supplier_name:
        add_supplier(connection, nif_code, supplier_name)
        # Clear the entries after insertion
        entry_nif.delete(0, tk.END)
        entry_name.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")

# Main program setup
connection = connect_to_database()
if connection is None:
    print("Failed to connect to the database. Exiting.")
else:
    # Set up the tkinter window
    root = tk.Tk()
    root.title("Add Supplier")
    
    # Labels and entry fields for Supplier_NIF_Code and Supplier_Name
    tk.Label(root, text="Supplier NIF Code:").grid(row=0, column=0, padx=10, pady=5)
    entry_nif = tk.Entry(root)
    entry_nif.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(root, text="Supplier Name:").grid(row=1, column=0, padx=10, pady=5)
    entry_name = tk.Entry(root)
    entry_name.grid(row=1, column=1, padx=10, pady=5)
    
    # Submit button
    submit_button = tk.Button(root, text="Add Supplier", command=submit)
    submit_button.grid(row=2, column=0, columnspan=2, pady=10)
    
    # Run the tkinter main loop
    root.mainloop()
    
    # Close the database connection after closing the GUI
    if connection.is_connected():
        connection.close()
        print("Database connection closed.")
