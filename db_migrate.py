from views import db
from _config import DATABASE_PATH
import sqlite3
from datetime import datetime
with sqlite3.connect(DATABASE_PATH) as connection:

    c=connection.cursor()
    c.execute("""ALTER TABLE customers RENAME TO old_customers""")

    db.create_all()

    c.execute("""SELECT name FROM old_customers ORDER BY customer_ID ASC""")

    data=[(row[0], 'scanmatics') for row in c.fetchall()]

    c.executemany("""INSERT INTO customers(name, company_id) VALUES(?,?)""", data)

    c.execute("DROP TABLE old_customers")