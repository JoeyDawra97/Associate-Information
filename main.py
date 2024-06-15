import tkinter as tk
from tkinter import ttk

def fetch_data():
    import psycopg2

    try:
        connection = psycopg2.connect(
            user="postgres",
            password="******",
            host="127.0.0.1",
            port="5432",
            database="website"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM associates_info")
        rows = cursor.fetchall()
        return rows

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_data(id, name, hire_date, manager, department):
    import psycopg2

    try:
        connection = psycopg2.connect(
            user="postgres",
            password="******",
            host="127.0.0.1",
            port="5432",
            database="website"
        )

        cursor = connection.cursor()
        insert_query = """INSERT INTO associates_info (ID, Name, Hire_Date, Manager, Department) 
                          VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (id, name, hire_date, manager, department))
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while inserting data into PostgreSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    # Refresh data in the table
    refresh_table()

def delete_data(id):
    import psycopg2

    try:
        connection = psycopg2.connect(
            user="postgres",
            password="******",
            host="127.0.0.1",
            port="5432",
            database="website"
        )

        cursor = connection.cursor()
        delete_query = """DELETE FROM associates_info WHERE ID = %s"""
        cursor.execute(delete_query, (id,))
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while deleting data from PostgreSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    # Refresh data in the table
    refresh_table()

def refresh_table():
    for i in tree.get_children():
        tree.delete(i)
    data = fetch_data()
    for row in data:
        tree.insert("", "end", values=row)

def on_insert_button_click():
    id = entry_id.get()
    name = entry_name.get()
    hire_date = entry_hire_date.get()
    manager = entry_manager.get()
    department = entry_department.get()

    insert_data(id, name, hire_date, manager, department)

def on_delete_button_click():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id = item['values'][0]
        delete_data(id)

def create_table_gui():
    global tree, entry_id, entry_name, entry_hire_date, entry_manager, entry_department

    root = tk.Tk()
    root.title("Associates Data")

    # Define style
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="gray")
    style.map('Treeview', background=[('selected', 'blue')])

    style.configure("Treeview.Heading",
                    background="blue",
                    foreground="yellow",
                    font=('Arial', 10, 'bold'))

    # Creating a treeview to display the data
    columns = ("col1", "col2", "col3", "col4", "col5")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    # Define headings
    tree.heading("col1", text="ID", anchor=tk.CENTER)
    tree.heading("col2", text="Name", anchor=tk.CENTER)
    tree.heading("col3", text="Hire Date", anchor=tk.CENTER)
    tree.heading("col4", text="Manager", anchor=tk.CENTER)
    tree.heading("col5", text="Department", anchor=tk.CENTER)

    # Centering the columns' data
    for col in columns:
        tree.column(col, anchor=tk.CENTER)

    # Inserting data into the treeview
    refresh_table()

    tree.pack(expand=True, fill='both')

    # Form for inserting new data
    form_frame = tk.Frame(root)
    form_frame.pack(fill='x', padx=10, pady=10)

    tk.Label(form_frame, text="ID").grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Name").grid(row=1, column=0, padx=5, pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Hire Date").grid(row=2, column=0, padx=5, pady=5)
    entry_hire_date = tk.Entry(form_frame)
    entry_hire_date.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Manager").grid(row=3, column=0, padx=5, pady=5)
    entry_manager = tk.Entry(form_frame)
    entry_manager.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Department").grid(row=4, column=0, padx=5, pady=5)
    entry_department = tk.Entry(form_frame)
    entry_department.grid(row=4, column=1, padx=5, pady=5)

    insert_button = tk.Button(form_frame, text="Insert", command=on_insert_button_click)
    insert_button.grid(row=5, column=0, columnspan=2, pady=10)

    # Delete button
    delete_button = tk.Button(root, text="Delete Selected", command=on_delete_button_click)
    delete_button.pack(pady=10)
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    create_table_gui()