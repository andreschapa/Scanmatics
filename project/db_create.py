import sqlite3
from _config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:
    c=connection.cursor()

    #creating table of customers
    c.execute("""CREATE TABLE customers(customer_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)""")

    c.execute(
        'INSERT INTO customers (name)'
        'VALUES("Scanmatics")'
    )
    
