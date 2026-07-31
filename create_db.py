import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    product_name TEXT NOT NULL,

    category TEXT NOT NULL,

    price REAL NOT NULL,

    stock INTEGER NOT NULL,

    description TEXT,

    image TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")