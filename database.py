from genericpath import exists
import sqlite3
from unittest.mock import DEFAULT

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ==========================
# USERS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    fullname TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    mobile TEXT NOT NULL,

    password TEXT NOT NULL,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("ALTER TABLE users ADD COLUMN address TEXT ;")

# ==========================
# ADMINS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================
# CATEGORIES TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category_name TEXT UNIQUE NOT NULL
)
""")

# ==========================
# PRODUCTS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    product_name TEXT NOT NULL,

    category TEXT NOT NULL,

    price REAL NOT NULL,

    stock INTEGER NOT NULL,

    description TEXT,

    image TEXT,

    vendor_id INTEGER,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================
# ORDERS TABLE
# ==========================

cursor.execute(""" 
CREATE TABLE IF NOT EXISTS orders( 
               
        id INTEGER PRIMARY KEY AUTOINCREMENT,
               
        user_id INTEGER NOT NULL,
               
        vendor_id INTEGER,
               
        product_id INTEGER NOT NULL, 
               
        fullname TEXT NOT NULL, 
               
        email TEXT NOT NULL, 
               
        mobile TEXT NOT NULL,
                
        address TEXT NOT NULL
               , 
        payment_method TEXT NOT NULL, 
               
        quantity INTEGER NOT NULL, 
               
        total_amount REAL NOT NULL, 
               
        status TEXT DEFAULT 'Pending', 
               
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
               
        FOREIGN KEY(user_id) REFERENCES users(id), 
               
        FOREIGN KEY(product_id) REFERENCES products(id) ) 
""")

# ==========================
# CART TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    product_id INTEGER,

    quantity INTEGER DEFAULT 1
)
""")

# ==========================
# WISHLIST TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS wishlist(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    product_id INTEGER
)
""")

# ==========================
# SETTINGS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    store_name TEXT,

    store_email TEXT,

    store_phone TEXT,

    store_address TEXT,

    currency TEXT
)
""")

#=========================
# CONTACT MESSAGES TABLE
#=========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS contact_messages(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL,

    subject TEXT NOT NULL,

    message TEXT NOT NULL,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
)
""")

#=========================
# ADDRESSES TABLE
#=========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    full_name TEXT NOT NULL,

    mobile TEXT NOT NULL,

    address_line TEXT NOT NULL,

    city TEXT NOT NULL,

    state TEXT NOT NULL,

    pincode TEXT NOT NULL,

    country TEXT DEFAULT 'India',

    FOREIGN KEY (user_id)
    REFERENCES users(id)
);
 """)

#=========================
# ORDER ITEMS TABLE
#=========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    order_id INTEGER NOT NULL,

    product_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    price REAL NOT NULL,

    FOREIGN KEY (order_id)
    REFERENCES orders(id),

    FOREIGN KEY (product_id)
    REFERENCES products(id)
);
""")

#=======================
# shipping address
#=======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS delivery_addresses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    address_type TEXT,

    receiver_name TEXT,

    mobile TEXT,

    address TEXT,

    city TEXT,

    state TEXT,

    pincode TEXT,

    is_default INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)

);  
""")

# ==========================
# NOTIFICATIONS TABLE
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    message TEXT NOT NULL,

    type TEXT DEFAULT 'info',

    is_read INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

#==========================
# VENDOR TABLE
#==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendors(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    store_name TEXT NOT NULL,

    owner_name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    mobile TEXT NOT NULL,

    password TEXT NOT NULL,

    gst_number TEXT,

    address TEXT,

    logo TEXT,

    status TEXT DEFAULT 'Pending',
               
    action TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
               """)

conn.commit()
conn.close()

print("All Tables Created Successfully")