from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

password = generate_password_hash("admin123")

cursor.execute("""
INSERT INTO admins
(username,password)
VALUES (?,?)
""", ("admin", password))

conn.commit()
conn.close()

print("Admin Created Successfully")