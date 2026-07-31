from flask import Flask, session, render_template, request, redirect, flash, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from functools import wraps
import sqlite3
import time
import os
import random
import smtplib
import uuid
from email.mime.text import MIMEText
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
#=================================================

def get_db_connection():

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    return conn

def send_otp(email):

    otp = random.randint(100000, 999999)

    message = MIMEText(
        f"""
        Hello,

        Your SHOPA password reset OTP is:

        {otp}

        This OTP is valid for 5 minutes.

        Do not share this OTP with anyone.
        """
    )

    message["Subject"] = "SHOPA Password Reset OTP"
    message["From"] = "yourmail@gmail.com"
    message["To"] = email


    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(
        "yourmail@gmail.com",
        "YOUR_APP_PASSWORD"
    )

    server.send_message(message)

    server.quit()


    return otp

def send_otp_email(email, otp):

    html_body = f"""
    <div style="
        max-width:500px;
        margin:auto;
        font-family:Arial,sans-serif;
        border:1px solid #ddd;
        border-radius:10px;
        overflow:hidden;
    ">

        <div style="
            background:#0f172a;
            color:white;
            text-align:center;
            padding:20px;
        ">

            <h1>SHOPA</h1>
            <p>Password Reset Request</p>

        </div>


        <div style="padding:30px;">

            <h2>Hello User,</h2>

            <p>
                You requested to reset your password.
            </p>

            <p>
                Use the OTP below to continue:
            </p>


            <div style="
                background:#2563eb;
                color:white;
                font-size:32px;
                font-weight:bold;
                text-align:center;
                padding:15px;
                border-radius:8px;
                letter-spacing:5px;
            ">

                {otp}

            </div>


            <p style="margin-top:20px;">
                This OTP will expire in 5 minutes.
            </p>

            <p>
                Do not share this OTP with anyone.
            </p>

        </div>


        <div style="
            background:#f1f5f9;
            text-align:center;
            padding:15px;
        ">

            © 2026 SHOPA. All Rights Reserved.

        </div>

    </div>
    """

    try:
        message = Message(
            subject="SHOPA Password Reset OTP",
            recipients=[email]
        )
        message.html = html_body
        mail.send(message)
        return True
    except Exception:
        return False

app = Flask(__name__)
app.secret_key = 'shopa_secret_key' 
mail = Mail(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "omkarmali2121@gmail.com"
app.config["MAIL_PASSWORD"] = "your_app_password"
app.config["MAIL_DEFAULT_SENDER"] = "omkarmali2121@gmail.com"
app.config["PRODUCT_UPLOAD_FOLDER"] = "static/uploads/products"
app.config["VENDOR_UPLOAD_FOLDER"] = "static/uploads/vendors"

#=============================
@app.route('/')
def welcome():
    return render_template('welcome.html')
#=============================


#=== User Route ========
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/products')
def products():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id DESC")

    products = cursor.fetchall()

    conn.close()

    return render_template(
        'products.html',
        products=products
    )

@app.route("/view-product/<int:id>")
def product_view(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (id,)
    )

    product = cursor.fetchone()

    conn.close()

    if not product:
        return "Product Not Found"

    return render_template(
        "product_view.html",
        product=product
    )

@app.route('/about')
def about():
    return render_template('user_about.html')

@app.route("/contact", methods=["GET","POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        print(name, email, subject, message)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO contact_messages
        (name,email,subject,message)
        VALUES (?,?,?,?)
        """,(name,email,subject,message))

        conn.commit()

        print("DATA SAVED")

        conn.close()

    return render_template("contact.html")

@app.route("/buy-now/<int:product_id>", methods=["GET", "POST"])
def buy_now(product_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Product Fetch

    cursor.execute(

        "SELECT * FROM products WHERE id=?",

        (product_id,)

    )

    product = cursor.fetchone()

    if product is None:

        conn.close()

        flash("Product not found.", "danger")

        return redirect("/products")

    quantity = 1

    total = product["price"] * quantity

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        mobile = request.form["mobile"]

        address = request.form["address"]

        payment = request.form["payment"]

        cursor.execute("""

        INSERT INTO orders(

            user_id,

            product_id,

            fullname,

            email,

            mobile,

            address,

            payment_method,

            quantity,

            total_amount

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """, (

            session["user_id"],

            product_id,

            fullname,

            email,

            mobile,

            address,

            payment,

            quantity,

            total

        ))

        conn.commit()

        conn.close()

        flash(

            "Order Placed Successfully!",

            "success"

        )

        return redirect("/my-orders")

    conn.close()

    return render_template(

        "checkout_buy_now.html",

        product=product,

        quantity=quantity,

        total=total

    )

@app.route("/checkout_cart", methods=["GET", "POST"])
def checkout():

    # ---------- Login Check ----------

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # ---------- Get Cart Products ----------

    cursor.execute("""
        SELECT

            cart.id,

            cart.quantity,

            products.id AS product_id,

            products.product_name AS name,

            products.price,

            products.image

        FROM cart

        JOIN products

        ON cart.product_id = products.id

        WHERE cart.user_id = ?

    """, (user_id,))

    cart_items = cursor.fetchall()

    # ---------- Empty Cart ----------

    if not cart_items:

        conn.close()

        flash("Your cart is empty.", "warning")

        return redirect("/cart")

    # ---------- Grand Total ----------

    total = 0

    for item in cart_items:

        total += item["price"] * item["quantity"]

    # ---------- Place Order ----------

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        mobile = request.form["mobile"]

        address = request.form["address"]

        payment = request.form["payment"]

        # Save Every Product

        for item in cart_items:

            cursor.execute("""
                INSERT INTO orders
                (
                    user_id,
                    product_id,
                    quantity,
                    fullname,
                    email,
                    mobile,
                    address,
                    payment_method,
                    total_amount
                )

                VALUES (?,?,?,?,?,?,?,?,?)

            """, (

                user_id,

                item["product_id"],

                item["quantity"],

                fullname,

                email,

                mobile,

                address,

                payment,

                item["price"] * item["quantity"]

            ))

        # ---------- Clear Cart ----------

        cursor.execute(

            "DELETE FROM cart WHERE user_id=?",

            (user_id,)

        )

        conn.commit()

        conn.close()

        flash(

            "Order Placed Successfully!",

            "success"

        )

        return redirect("/my-orders")

    conn.close()

    return render_template(

        "checkout_cart.html",

        cart_items=cart_items,

        total=total

    )

@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:

        flash("Please login first.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            orders.*,

            products.product_name,

            products.image,

            products.price

        FROM orders

        JOIN products

        ON orders.product_id = products.id

        WHERE orders.user_id=?

        ORDER BY orders.id DESC

    """, (session["user_id"],))

    orders = cursor.fetchall()

    conn.close()

    return render_template(

        "my_orders.html",

        orders=orders

    )

@app.route("/order/<int:order_id>")
def order_details(order_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            orders.*,

            products.product_name,

            products.image,

            products.price,

            products.description

        FROM orders

        JOIN products

        ON orders.product_id = products.id

        WHERE
            orders.id=?
        AND
            orders.user_id=?

    """,(order_id, session["user_id"]))

    order = cursor.fetchone()

    conn.close()

    if order is None:

        flash("Order not found.","danger")

        return redirect("/my-orders")

    return render_template(

        "order_details.html",

        order=order

    )

@app.route("/cancel-order/<int:order_id>")
def cancel_order(order_id):

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Check Order

    cursor.execute("""

        SELECT *

        FROM orders

        WHERE id=?

        AND user_id=?

    """,(order_id, user_id))

    order = cursor.fetchone()

    if order is None:

        conn.close()

        flash("Order not found.", "danger")

        return redirect("/my-orders")

    # Allow only Pending or Confirmed

    if order["status"] not in ["Pending","Confirmed"]:

        conn.close()

        flash(

            "This order cannot be cancelled.",

            "danger"

        )

        return redirect("/my-orders")

    # Update Status

    cursor.execute("""

        UPDATE orders

        SET status=?

        WHERE id=?

    """,(

        "Cancelled",

        order_id

    ))

    conn.commit()

    conn.close()

    flash(

        "Order Cancelled Successfully.",

        "success"

    )

    return redirect("/my-orders")

@app.route("/download-invoice/<int:order_id>")
def download_invoice(order_id):

    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            orders.*,
            products.product_name,
            products.price
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE orders.id=?
    """, (order_id,))

    order = cursor.fetchone()

    conn.close()
    if not order:
        flash("Invoice not found", "danger")
        return redirect("/my-orders")

    filename = f"invoice_{order_id}.pdf"
    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        rightMargin=25,

        leftMargin=25,

        topMargin=25,

        bottomMargin=25

    )

    styles = getSampleStyleSheet()

    elements = []
    # ==========================
    # SHOPA HEADER WITH LOGO
    # ==========================

    logo = Image(
        "static/images/SOPA.png",
        width=1.2 * inch,
        height=1.2 * inch
    )

    company = Paragraph("""

    <font size="22" color="#0d6efd">
    <b>SHOPA</b>
    </font>

    <br/>

    <font size="11">

    Professional E-Commerce Store

    <br/>

    support@shopa.com

    <br/>

    www.shopa.com

    </font>

    """, styles["Normal"])

    header = Table(
        [
            [logo, company]
        ],
        colWidths=[90, 340]
    )

    header.setStyle(TableStyle([

        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("BOTTOMPADDING", (0,0), (-1,-1), 20)

    ]))

    elements.append(header)
    # ==========================
    # CUSTOMER DETAILS
    # ==========================

    customer_title = Paragraph(

        "<b><font size='14'>Bill To</font></b>",

        styles["Heading2"]

    )

    elements.append(customer_title)

    elements.append(Spacer(1,8))
    customer_data = [

    ["Customer", order["fullname"]],

    ["Email", order["email"]],

    ["Mobile", order["mobile"]],

    ["Address", order["address"]]

    ]

    customer_table = Table(

        customer_data,

        colWidths=[120,310]

    )

    customer_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#198754")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.beige),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,-1),10),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),11)

        ])

    )

    elements.append(customer_table)

    elements.append(Spacer(1,20))
    # ==========================
    # PRODUCT DETAILS
    # ==========================

    product_title = Paragraph(

        "<b><font size='14'>Product Details</font></b>",

        styles["Heading2"]

    )

    elements.append(product_title)

    elements.append(Spacer(1,8))
    product_data = [

    [

        "Product",

        "Qty",

        "Price",

        "Total"

    ],

    [

        order["product_name"],

        str(order["quantity"]),

        f"₹ {order['price']:.2f}",

        f"₹ {order['total_amount']:.2f}"

    ]

    ]

    product_table = Table(

        product_data,

        colWidths=[220,60,80,90]

    )

    product_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0d6efd")),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("ALIGN",(1,0),(-1,-1),"CENTER"),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,0),12),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("FONTNAME",(0,1),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),11)

        ])

    )

    elements.append(product_table)

    elements.append(Spacer(1,20))
    # ==========================
    # ORDER SUMMARY
    # ==========================

    summary_title = Paragraph(

        "<b><font size='14'>Order Summary</font></b>",

        styles["Heading2"]

    )

    elements.append(summary_title)

    elements.append(Spacer(1,8))

    summary_data = [

    [

        "Subtotal",

        f"₹ {order['total_amount']:.2f}"

    ],

    [

        "Shipping",

        "FREE"

    ],

    [

        "Discount",

        "₹ 0.00"

    ],

    [

        "Grand Total",

        f"₹ {order['total_amount']:.2f}"

    ]

    ]

    summary_table = Table(

        summary_data,

        colWidths=[250,150]

    )

    summary_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,-2),colors.whitesmoke),

            ("BACKGROUND",(0,3),(-1,3),colors.HexColor("#198754")),

            ("TEXTCOLOR",(0,3),(-1,3),colors.white),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("ALIGN",(1,0),(1,-1),"RIGHT"),

            ("BOTTOMPADDING",(0,0),(-1,-1),12),

            ("TOPPADDING",(0,0),(-1,-1),12),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),11)

        ])

    )

    elements.append(summary_table)

    elements.append(Spacer(1,20))
    # ==========================
    # PAYMENT & STATUS
    # ==========================

    payment_title = Paragraph(

        "<b><font size='14'>Payment Information</font></b>",

        styles["Heading2"]

    )

    elements.append(payment_title)

    elements.append(Spacer(1,8))
    status = order["status"]

    if status == "Pending":
        status_color = "#FFC107"

    elif status == "Confirmed":
        status_color = "#0D6EFD"

    elif status == "Shipped":
        status_color = "#FD7E14"

    elif status == "Delivered":
        status_color = "#198754"

    else:
        status_color = "#DC3545"
    
    payment_data = [

    [

        "Payment Method",

        order["payment_method"]

    ],

    [

        "Order Status",

        f"{status}"

    ]

    ]

    payment_table = Table(

        payment_data,

        colWidths=[180,220]

    )

    payment_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#0d6efd")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.whitesmoke),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,-1),10),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),11)

        ])

    )

    elements.append(payment_table)

    elements.append(Spacer(1,25))
    # ==========================
    # FOOTER
    # ==========================

    footer_title = Paragraph(

        "<b><font size='16' color='#0d6efd'>Thank You For Shopping With SHOPA ❤️</font></b>",

        styles["Title"]

    )

    elements.append(footer_title)

    elements.append(Spacer(1,15))
    footer_data = [

    ["Customer Support", "support@shopa.com"],

    ["Website", "www.shopa.com"],

    ["Phone", "+91 9876543210"],

    ["Working Hours", "Mon - Sat | 9:00 AM - 7:00 PM"]

    ]

    footer_table = Table(

        footer_data,

        colWidths=[150,250]

    )

    footer_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#0d6efd")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.whitesmoke),

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BOTTOMPADDING",(0,0),(-1,-1),10),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),11)

        ])

    )

    elements.append(footer_table)

    elements.append(Spacer(1,20))
    note = Paragraph(

    """
    <para align='center'>

    <font size='10' color='grey'>

    This is a computer generated invoice.<br/>

    No signature is required.<br/><br/>

    © 2026 SHOPA. All Rights Reserved.

    </font>

    </para>

    """,

    styles["Normal"]

    )

    elements.append(note)

    doc.build(elements)

    return send_file(
        filename,
        as_attachment=True,
        download_name=f"Invoice_{order_id}.pdf",
        mimetype="application/pdf"
    )

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    user_id = session["user_id"]

    # User Details
    cursor.execute("""
        SELECT *
        FROM users
        WHERE id=?
    """, (user_id,))
    user = cursor.fetchone()

    # Total Orders
    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE user_id=?
    """, (user_id,))
    total_orders = cursor.fetchone()[0]

    # Pending Orders
    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE user_id=?
        AND status='Pending'
    """, (user_id,))
    pending_orders = cursor.fetchone()[0]

    # Wishlist Items
    cursor.execute("""
        SELECT COUNT(*)
        FROM wishlist
        WHERE user_id=?
    """, (user_id,))
    wishlist_items = cursor.fetchone()[0]

    # Total Spending
    cursor.execute("""
        SELECT IFNULL(SUM(total_amount),0)
        FROM orders
        WHERE user_id=?
        AND status='Delivered'
    """, (user_id,))
    total_spending = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute("""
        SELECT
            orders.id,
            products.product_name,
            orders.status,
            orders.total_amount
        FROM orders
        JOIN products
        ON orders.product_id=products.id
        WHERE orders.user_id=?
        ORDER BY orders.id DESC
        LIMIT 5
    """, (user_id,))

    recent_orders = cursor.fetchall()

    conn.close()

    return render_template(
        "user_profile.html",
        user=user,
        total_orders=total_orders,
        pending_orders=pending_orders,
        wishlist_items=wishlist_items,
        total_spending=total_spending,
        recent_orders=recent_orders
    )

@app.route("/profile/update")
def update_profile():
    return render_template("user_profile_update.html")

@app.route("/delivery-address", methods=["GET", "POST"])
def delivery_address():

    if request.method == "POST":

        address_type = request.form["address_type"]
        receiver_name = request.form["receiver_name"]
        mobile = request.form["mobile"]
        city = request.form["city"]
        state = request.form["state"]
        pincode = request.form["pincode"]
        address = request.form["address"]

        is_default = (
            True if "default" in request.form
            else False
        )

        flash(
            "Delivery address saved successfully!",
            "success"
        )

        return redirect("/delivery-address")


    return render_template(
        "/delivery_address.html"
    )

@app.route("/add-address", methods=["GET","POST"])
def add_new_address():

    return render_template(
        "/user_add-address.html"
    )

@app.route("/update_address/<int:id>", methods=["GET", "POST"])
def update_address(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    if request.method == "POST":

        address_type = request.form["address_type"]
        receiver_name = request.form["receiver_name"]
        mobile = request.form["mobile"]
        city = request.form["city"]
        state = request.form["state"]
        pincode = request.form["pincode"]
        full_address = request.form["address"]

        is_default = 1 if "default" in request.form else 0

        cursor.execute("""
            UPDATE delivery_addresses
            SET address_type=?,
                receiver_name=?,
                mobile=?,
                city=?,
                state=?,
                pincode=?,
                address=?,
                is_default=?
            WHERE id=?
        """, (
            address_type,
            receiver_name,
            mobile,
            city,
            state,
            pincode,
            full_address,
            is_default,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Address updated successfully!",
            "success"
        )

        return redirect("/delivery_address")

    cursor.execute(
        "SELECT * FROM delivery_addresses WHERE id=?",
        (id,)
    )

    address = cursor.fetchone()
    conn.close()

    return render_template(
        "/update_address.html",
        address=address
    )

@app.route("/wishlist")
def wishlist():

    if not session.get("user_id"):
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT

        wishlist.id,

        products.id as product_id,

        products.product_name as name,

        products.price,

        products.image

        FROM wishlist

        JOIN products
        ON wishlist.product_id = products.id

        WHERE wishlist.user_id = ?

    """, (user_id,))

    wishlist_items = cursor.fetchall()

    conn.close()

    return render_template(
        "wishlist.html",
        wishlist_items=wishlist_items
    )

@app.route("/wishlist/add/<int:product_id>")
def add_to_wishlist(product_id):

    if not session.get("user_id"):

        flash(
            "Please login first",
            "danger"
        )

        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM wishlist
        WHERE user_id=?
        AND product_id=?
        """,
        (user_id, product_id)
    )

    existing = cursor.fetchone()

    if not existing:

        cursor.execute(
            """
            INSERT INTO wishlist
            (
                user_id,
                product_id
            )
            VALUES (?,?)
            """,
            (user_id, product_id)
        )

        conn.commit()

    conn.close()

    flash(
        "Added to Wishlist ❤️",
        "success"
    )

    return redirect("/products")

@app.route("/wishlist/remove/<int:id>")
def remove_wishlist(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM wishlist WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/wishlist")

@app.context_processor
def wishlist_counter():

    if not session.get("user_id"):

        return {
            "wishlist_count": 0
        }

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM wishlist
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return {
        "wishlist_count": count
    }

@app.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):

    if not session.get("user_id"):

        flash("Please login first", "danger")

        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cart
        WHERE user_id = ?
        AND product_id = ?
        """,
        (user_id, product_id)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE cart
            SET quantity = quantity + 1
            WHERE user_id = ?
            AND product_id = ?
            """,
            (user_id, product_id)
        )

    else:

        cursor.execute(
            """
            INSERT INTO cart
            (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            """,
            (user_id, product_id, 1)
        )

    conn.commit()
    conn.close()

    flash(
        "Product added to cart successfully",
        "success"
    )

    return redirect("/products")

@app.route("/cart/increase/<int:cart_id>")
def increase_quantity(cart_id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE cart
        SET quantity = quantity + 1
        WHERE id = ?
        """,
        (cart_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/cart")

@app.route("/cart/decrease/<int:cart_id>")
def decrease_quantity(cart_id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT quantity FROM cart WHERE id=?",
        (cart_id,)
    )

    item = cursor.fetchone()

    if item and item[0] > 1:

        cursor.execute(
            """
            UPDATE cart
            SET quantity = quantity - 1
            WHERE id = ?
            """,
            (cart_id,)
        )

    conn.commit()
    conn.close()

    return redirect("/cart")

@app.route("/cart/remove/<int:cart_id>")
def remove_from_cart(cart_id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE id = ?",
        (cart_id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Product removed from cart",
        "success"
    )

    return redirect("/cart")

@app.route('/cart')
def cart():

    if not session.get("user_id"):

        return redirect("/login")


    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cart.id,
            cart.quantity,
            products.product_name,
            products.price,
            products.image
        FROM cart

        JOIN products
        ON cart.product_id = products.id

        WHERE cart.user_id = ?
    """, (user_id,))

    cart_items = cursor.fetchall()

    total = 0

    for item in cart_items:

        total += item["price"] * item["quantity"]

    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/payment-success")
def payment_success():
    return """
    <h2>
    Payment Successful 🎉
    </h2>
    """

@app.route("/user/settings", methods=["GET", "POST"])
def user_settings():

    user_id = 1 

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        address = request.form["address"]
        password = request.form["password"]

        if password:

            password = generate_password_hash(password)

            cursor.execute("""
            UPDATE users
            SET fullname=?,
                email=?,
                mobile=?,
                address=?,
                password=?
            WHERE id=?
            """,

            (fullname,email,mobile,address,password,user_id))

        else:
            cursor.execute("""
            UPDATE users
            SET fullname=?,
                email=?,
                mobile=?,
                address=?
            WHERE id=?
            """,

            (fullname,email,mobile,address,user_id))

        conn.commit()
    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()
    conn.close()
    return render_template(
        "user_settings.html",
        user=user
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (fullname,email,mobile,password)
            VALUES (?,?,?,?)
        """, (
            fullname,
            email,
            mobile,
            hashed_password
        ))

        conn.commit()
        conn.close()

        flash("Registration Successful", "success")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id,password
            FROM users
            WHERE email=?
            """,(email,))

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[1], password):

            session["user_id"] = user[0]

            flash("Login Successful", "success")

            return redirect("/home")

        flash("Invalid Email or Password", "danger")

    return render_template('login.html')

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        otp = random.randint(100000, 999999)

        email_sent = send_otp_email(email, otp)

        session["otp"] = str(otp)
        session["email"] = email
        session["reset_email"] = email

        # OTP Generate Time
        session["otp_time"] = time.time()

        # OTP Attempts
        session["otp_attempt"] = 0

        flash(
            "Password reset link sent to your email." if email_sent else "OTP generated successfully. Email delivery is currently unavailable, but the OTP is ready for local testing.",
            "success" if email_sent else "warning"
        )

        return redirect("/verify-otp")

    return render_template("forgot_password.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        user_otp = request.form["otp"]

        if time.time() - session.get("otp_time", 0) > 300:

            session.pop("otp", None)

            flash(
                "OTP Expired. Please request a new OTP.",
                "danger"
            )

            return redirect("/forgot-password")

        if session["otp_attempt"] >= 5:

            session.clear()

            flash(
                "Too many wrong attempts. Try again later.",
                "danger"
            )

            return redirect("/forgot-password")

        if user_otp != session["otp"]:

            session["otp_attempt"] += 1

            remaining = 5 - session["otp_attempt"]

            flash(
                f"Wrong OTP. {remaining} attempts left.",
                "danger"
            )

            return redirect("/verify-otp")

        session["otp_verified"] = True

        flash(
            "OTP Verified Successfully!",
            "success"
        )

        return redirect("/create-new-password")

    return render_template("otp_verification.html")

@app.route("/create-new-password", methods=["GET", "POST"])
def create_new_password():

    if request.method == "POST":

        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:

            flash(
                "Passwords do not match",
                "danger"
            )

            return redirect("/create-new-password")


        hashed_password = generate_password_hash(
            new_password
        )

        print("New Password Hash:", hashed_password)

        session.pop("otp", None)
        session.pop("reset_email", None)
        session.pop("otp_verified", None)
        session.pop("otp_time", None)
        session.pop("otp_attempt", None)

        flash(
            "Password updated successfully. Please login.",
            "success"
        )

        return redirect("/login")

    return render_template("create_new_password.html")

@app.route("/sign-out")
def logout():

    session.clear()

    return redirect("/login")

#====================================================================================

#==== Admin Route ===================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "Omkar" and password == "Omkar@123":

            flash("Login Successfully...")

            return redirect("/admin/dashboard")

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    flash("Sign-out Successfully...")

    return redirect("/admin/login")

@app.context_processor
def admin_notifications():

    try:

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM notifications
            ORDER BY id DESC
            LIMIT 10
        """)

        notifications = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE is_read=0
        """)

        notification_count = cursor.fetchone()[0]

        conn.close()

    except:

        notifications = []
        notification_count = 0

    return dict(

        notifications=notifications,

        notification_count=notification_count

    )

@app.route("/admin/notifications/read-all")
def read_all_notifications():

    conn=sqlite3.connect("database.db")

    cursor=conn.cursor()

    cursor.execute("""

    UPDATE notifications

    SET is_read=1

    WHERE is_read=0

    """)

    conn.commit()

    conn.close()

    return redirect(request.referrer or "/admin/dashboard")
   
@app.route("/admin/dashboard")
def admin_dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total Orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("""
        SELECT IFNULL(SUM(total_amount),0)
        FROM orders
        WHERE status='Delivered'
    """)

    total_revenue = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute("""
        SELECT
            orders.id,
            orders.fullname,
            orders.total_amount,
            orders.status
        FROM orders
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_orders = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_products=total_products,
        total_orders=total_orders,
        total_users=total_users,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        active_page="dashboard"
    )

@app.route("/admin/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]
        image = request.files["image"]

        filename = ""
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

        def allowed_file(filename):
            return "." in filename and \
                  filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

        if image and image.filename != "":
            filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
            os.makedirs(
                app.config["PRODUCT_UPLOAD_FOLDER"],
                exist_ok=True
            )

            image.save(
                os.path.join(
                    app.config["PRODUCT_UPLOAD_FOLDER"],
                    filename
                )
            )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (
                product_name,
                category,
                price,
                stock,
                description,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            category,
            price,
            stock,
            description,
            filename
        ))

        conn.commit()

        cursor.execute("""
        INSERT INTO notifications
        (
            title,
            message,
            type
        )
        VALUES (?,?,?)
        """,(

            "New Product",

            f"{product_name} added successfully.",

            "success"

        ))
        conn.commit()
        conn.close()

        flash(
            "Product added successfully!",
            "admin_success"
        )

        return redirect("/admin/products")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM categories"
    )

    categories = cursor.fetchall()
    conn.close()

    return render_template(
        "admin_add-product.html",
        categories=categories,
        active_page="products"
    )

@app.route("/admin/delete-product/<int:id>")
def delete_product(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Image Name
    cursor.execute(
        "SELECT image FROM products WHERE id=?",
        (id,)
    )

    product = cursor.fetchone()

    if product:

        image_path = os.path.join(
            app.config["PRODUCT_UPLOAD_FOLDER"],
            product["image"]
        )

        if os.path.exists(image_path):
            os.remove(image_path)

        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (id,)
        )

        conn.commit()

    conn.close()

    flash(
        "Product Deleted Successfully!",
        "success"
    )

    return redirect("/admin/products")

@app.route("/admin/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]

        image = request.files["image"]

        # Old Image
        cursor.execute(
            "SELECT image FROM products WHERE id=?",
            (id,)
        )

        product = cursor.fetchone()

        filename = product["image"]

        # New Image Upload
        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["PRODUCT_UPLOAD_FOLDER"],
                    filename
                )
            )

        cursor.execute("""
            UPDATE products
            SET
                product_name=?,
                category=?,
                price=?,
                stock=?,
                description=?,
                image=?
            WHERE id=?
        """,
        (
            product_name,
            category,
            price,
            stock,
            description,
            filename,
            id
        ))

        conn.commit()

        cursor.execute("""
            INSERT INTO notifications
            (
                title,
                message,
                type
            )
            VALUES (?,?,?)
            """,(

                "New Product",

                f"{product_name}  added.",

                "success"

            ))
        
        conn.commit()

        conn.close()

        flash(
            "Product Updated Successfully!",
            "success"
        )

        return redirect("/admin/products")

    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    )

    product = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_edit_product.html",
        product=product,
        active_page="products"
    )                

@app.route("/admin/products")  
def manage_products():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_products.html",
        products=products,
        active_page="products"
    )

@app.route("/admin/products/manage")
def manage():
    return render_template("manage_product.html")

@app.route("/admin/categories", methods=["GET", "POST"])
def manage_categories():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        category_name = request.form["category_name"]

        cursor.execute(
            "INSERT INTO categories(category_name) VALUES(?)",
            (category_name,)
        )

        conn.commit()
        cursor.execute("""
        INSERT INTO notifications
        (
            title,
            message,
            type
        )
        VALUES (?,?,?)
        """,(

            "New Category",

            f"{category_name} category added.",

            "success"

        ))
        conn.commit()

        flash(
            "Category Added Successfully!",
            "admin_success"
        )

    cursor.execute(
        "SELECT * FROM categories ORDER BY id DESC"
    )

    categories = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_categories.html",
        categories=categories,
        active_page="categories"
    )

@app.route("/admin/edit-category/<int:id>", methods=["GET", "POST"])
def edit_category(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    if request.method == "POST":

        category_name = request.form["category_name"]

        cursor.execute("""
            UPDATE categories
            SET category_name=?
            WHERE id=?
        """,
        (
            category_name,
            id
        ))

        conn.commit()
        cursor.execute("""
            INSERT INTO notifications
            (
                title,
                message,
                type
            )
            VALUES (?,?,?)
        """, (
            "Category Updated",
            f"Category '{category_name}' updated.",
            "info"
        ))
        conn.commit()
        conn.close()

        flash(
            "Category Updated Successfully!",
            "success"
        )

        return redirect("/admin/categories")

    cursor.execute(
        "SELECT * FROM categories WHERE id=?",
        (id,)
    )

    category = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_edit_category.html",
        category=category,
        active_page="categories"
    )

@app.route("/admin/delete-category/<int:id>")
def delete_category(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM categories WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Category Deleted Successfully!",
        "success"
    )

    return redirect("/admin/categories")

@app.route("/admin/orders")
def manage_orders():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            orders.id,
            orders.fullname,
            products.product_name,
            orders.total_amount,
            orders.status,
            orders.order_date
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        ORDER BY orders.id DESC
    """)

    orders = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders,
        active_page="orders"
    )

@app.route("/admin/order/<int:id>")
def admin_order_details(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE id=?",
        (id,)
    )

    order = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_order_details.html",
        order=order,
        active_page="orders"
    )

@app.route("/admin/order-status/<int:id>/<status>")
def update_order_status(id, status):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status=?
        WHERE id=?
    """, (status, id))

    conn.commit()

    cursor.execute("""
        INSERT INTO notifications
        (
            title,
            message,
            type
        )
        VALUES (?,?,?)
        """,(

            "Order Updated",

            f"Order #{id} marked as {status}.",

            "info"

        ))
    conn.commit()
    conn.close()


    flash(
        "Order Status Updated Successfully!",
        "success"
    )

    return redirect("/admin/orders")

@app.route("/admin/users")
def manage_users():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            fullname,
            email,
            mobile,
            created_at
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_users.html",
        users=users,
        active_page="users"
    )

@app.route("/admin/view-user/<int:user_id>")
def view_user(user_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        flash("User not found!", "danger")
        return redirect("/admin/users")

    return render_template(
        "admin_view_user.html",
        user=user,
        active_page="users"
    )

@app.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("User deleted successfully!", "success")

    return redirect("/admin/users")

@app.route("/admin/sales-report")
def sales_report():
    return render_template("admin_sales_report.html")

@app.route("/admin/revenue")
def revenue_analytics():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(total)
    FROM orders
    """)
    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    """)
    total_orders = cursor.fetchone()[0]

    avg_order = (
        round(total_revenue / total_orders, 2)
        if total_orders > 0 else 0
    )

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE status='Delivered'
    """)
    delivered_orders = cursor.fetchone()[0]

    months = [
        "Jan","Feb","Mar",
        "Apr","May","Jun",
        "Jul","Aug","Sep",
        "Oct","Nov","Dec"
    ]

    revenue_data = [
        25000,40000,35000,
        60000,70000,55000,
        80000,90000,75000,
        95000,100000,120000
    ]

    conn.close()

    return render_template(
        "admin_revenue.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        avg_order=avg_order,
        delivered_orders=delivered_orders,
        months=months,
        revenue_data=revenue_data,
        active_page="dashboard"
    )

@app.route("/admin/messages")
def admin_messages():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM contact_messages
    ORDER BY id DESC
    """)

    messages = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_messages.html",
        messages=messages,
        active_page="messages"
    )

@app.route("/admin/message/<int:id>")
def view_message(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM contact_messages WHERE id=?",
        (id,)
    )

    message = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_view_message.html",
        message=message,
        active_page="messages"
    )

@app.route("/admin/reply-message/<int:id>",
           methods=["GET","POST"])
def reply_message(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM contact_messages WHERE id=?",
        (id,)
    )

    message = cursor.fetchone()

    if request.method=="POST":

        subject=request.form["subject"]

        reply=request.form["reply"]

        email=message["email"]

        msg=MIMEText(reply)

        msg["Subject"]=subject

        msg["From"]="yourgmail@gmail.com"

        msg["To"]=email

        server=smtplib.SMTP("smtp.gmail.com",587)

        server.starttls()

        server.login(
            "yourgmail@gmail.com",
            "your-app-password"
        )

        server.send_message(msg)

        server.quit()

        flash(
            "Reply Sent Successfully!",
            "success"
        )

        conn.close()

        return redirect("/admin/messages")

    conn.close()

    return render_template(
        "admin_reply_message.html",
        message=message,
        active_page="messages"
    )

@app.route("/admin/delete-message/<int:id>")
def delete_message(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM contact_messages WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Message Deleted Successfully!",
        "success"
    )

    return redirect("/admin/messages")

@app.route("/admin/settings", methods=["GET","POST"])
def admin_settings():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        store_name = request.form["store_name"]
        store_email = request.form["store_email"]
        store_phone = request.form["store_phone"]
        store_address = request.form["store_address"]
        currency = request.form["currency"]

        cursor.execute("DELETE FROM settings")

        cursor.execute("""
        INSERT INTO settings
        (
            store_name,
            store_email,
            store_phone,
            store_address,
            currency
        )
        VALUES(?,?,?,?,?)
        """,(
            store_name,
            store_email,
            store_phone,
            store_address,
            currency
        ))

        conn.commit()

    cursor.execute("""
    SELECT * FROM settings
    LIMIT 1
    """)

    settings = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_settings.html",
        settings=settings,
        active_page="settings"
    )

#====================================================


#==== Vendor Route ==================================

@app.route("/admin/vendors")
def admin_vendors():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM vendors

        ORDER BY id DESC

    """)

    vendors = cursor.fetchall()

    conn.close()

    return render_template(

        "admin_vendors.html",

        vendors=vendors,

        active_page="vendors"

    )

@app.route("/admin/vendor-status/<int:vendor_id>/<status>")
def vendor_status(vendor_id, status):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE vendors

        SET status=?

        WHERE id=?

    """, (status, vendor_id))

    conn.commit()

    conn.close()

    flash("Vendor status updated successfully.", "success")

    return redirect("/admin/vendors")

@app.route("/admin/delete-vendor/<int:vendor_id>")
def delete_vendor(vendor_id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM vendors

        WHERE id=?

    """, (vendor_id,))

    conn.commit()

    conn.close()

    flash("Vendor deleted successfully.", "success")

    return redirect("/admin/vendors")

@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():

    if request.method == "POST":

        store_name = request.form["store_name"]
        owner_name = request.form["owner_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        gst_number = request.form["gst_number"]
        address = request.form["address"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect("/vendor/register")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM vendors WHERE email=?",
            (email,)
        )

        vendor = cursor.fetchone()

        if vendor:

            conn.close()

            flash(
                "Email already registered.",
                "vendor_warning"
            )

            return redirect("/vendor/register")

        logo = request.files["logo"]

        filename = ""

        if logo and logo.filename != "":

            filename = secure_filename(
                logo.filename
            )

            logo.save(

                os.path.join(

                    app.config["VENDOR_UPLOAD_FOLDER"],

                    filename

                )

            )

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute("""

        INSERT INTO vendors(

            store_name,
            owner_name,
            email,
            mobile,
            password,
            gst_number,
            address,
            logo,
            status

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """,

        (

            store_name,

            owner_name,

            email,

            mobile,

            hashed_password,

            gst_number,

            address,

            filename,

            "Pending"

        )

        )

        conn.commit()

        conn.close()

        flash(

            "Registration successful. Wait for Admin Approval.",

            "vendor_success"

        )

        return redirect("/vendor/login")

    return render_template(

        "/vendor_register.html"

    )

@app.route("/vendor/login", methods=["GET", "POST"])
def vendor_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""

        SELECT *

        FROM vendors

        WHERE email=?

        """,(email,))

        vendor = cursor.fetchone()

        conn.close()

        if not vendor:

            flash(

                "Invalid Email.",

                "vendor_danger"

            )

            return redirect("/vendor/login")

        if not check_password_hash(

            vendor["password"],

            password

        ):

            flash(

                "Incorrect Password.",

                "vendor_danger"

            )

            return redirect("/vendor/login")

        if vendor["status"] != "Approved":

            flash(

                "Your account is under review by Admin.",

                "vendor_warning"

            )

            return redirect("/vendor/login")

        session["vendor_id"] = vendor["id"]

        session["vendor_name"] = vendor["store_name"]

        flash(

            "Welcome Vendor!",

            "vendor_success"

        )

        return redirect("/vendor/dashboard")

    return render_template(

        "vendor_login.html"

    )

@app.route("/vendor/forgot-password", methods=["GET", "POST"])
def vendor_forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        if not email:
            flash("Please enter your email address.", "vendor_danger")
            return redirect("/vendor/forgot-password")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM vendors WHERE email=?", (email,))
        vendor = cursor.fetchone()
        conn.close()

        if not vendor:
            flash("No vendor account found with that email.", "vendor_danger")
            return redirect("/vendor/forgot-password")

        otp = random.randint(100000, 999999)

        email_sent = send_otp_email(email, otp)

        session["otp"] = str(otp)
        session["email"] = email
        session["otp_time"] = time.time()
        session["otp_attempt"] = 0
        session["reset_type"] = "vendor"

        flash("Password reset OTP sent to your email." if email_sent else "OTP generated successfully. Email delivery is currently unavailable, but the OTP is ready for local testing.", "vendor_success" if email_sent else "vendor_warning")
        return redirect("/vendor/verify-otp")

    return render_template("vendor_forgot_password.html")

@app.route("/vendor/verify-otp", methods=["GET", "POST"])
def vendor_verify_otp():

    if request.method == "POST":

        user_otp = request.form.get("otp", "").strip()

        if time.time() - session.get("otp_time", 0) > 300:
            session.pop("otp", None)
            flash("OTP expired. Please request a new OTP.", "vendor_danger")
            return redirect("/vendor/forgot-password")

        if session.get("otp_attempt", 0) >= 5:
            session.clear()
            flash("Too many wrong attempts. Try again later.", "vendor_danger")
            return redirect("/vendor/forgot-password")

        if user_otp != session.get("otp"):
            session["otp_attempt"] = session.get("otp_attempt", 0) + 1
            remaining = 5 - session["otp_attempt"]
            flash(f"Wrong OTP. {remaining} attempts left.", "vendor_danger")
            return redirect("/vendor/verify-otp")

        session["otp_verified"] = True
        flash("OTP verified successfully!", "vendor_success")
        return redirect("/vendor/create-new-password")

    return render_template("otp_verification.html")

@app.route("/vendor/create-new-password", methods=["GET", "POST"])
def vendor_create_new_password():

    if request.method == "POST":

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "vendor_danger")
            return redirect("/vendor/create-new-password")

        if not session.get("otp_verified"):
            flash("Please verify the OTP first.", "vendor_danger")
            return redirect("/vendor/forgot-password")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "UPDATE vendors SET password=? WHERE email=?",
            (hashed_password, session.get("email"))
        )

        conn.commit()
        conn.close()

        session.pop("otp_verified", None)
        session.pop("otp", None)
        session.pop("email", None)
        session.pop("otp_time", None)
        session.pop("otp_attempt", None)
        session.pop("reset_type", None)

        flash("Password reset successfully. Please login again.", "vendor_success")
        return redirect("/vendor/login")

    return render_template("create_new_password.html")

@app.route("/admin/vendor/<int:vendor_id>")
def view_vendor(vendor_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM vendors

        WHERE id=?

    """, (vendor_id,))

    vendor = cursor.fetchone()

    conn.close()

    if vendor is None:

        flash("Vendor not found.", "danger")

        return redirect("/admin/vendors")

    return render_template(

        "admin_view_vendor.html",

        vendor=vendor,

        active_page="vendors"

    )

@app.route("/vendor/dashboard")
def vendor_dashboard():

    if "vendor_id" not in session:

        flash("Please login first.", "vendor_warning")

        return redirect("/vendor/login")

    vendor_id = session["vendor_id"]

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE vendor_id=?
    """, (vendor_id,))
    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
    """, (vendor_id,))
    total_orders = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
        AND orders.status='Pending'
    """, (vendor_id,))
    pending_orders = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
        IFNULL(SUM(orders.total_amount),0)

        FROM orders

        JOIN products

        ON orders.product_id=products.id

        WHERE products.vendor_id=?
        AND orders.status='Delivered'
    """, (vendor_id,))

    total_revenue = cursor.fetchone()[0]

    cursor.execute("""

    SELECT

    orders.id,
    orders.fullname,
    products.product_name,
    orders.quantity,
    orders.total_amount,
    orders.status,
    orders.order_date

    FROM orders

    JOIN products

    ON orders.product_id = products.id

    WHERE products.vendor_id=?

    ORDER BY orders.id DESC

    LIMIT 5

    """, (vendor_id,))

    recent_orders = cursor.fetchall()

    conn.close()

    return render_template(

        "/vendor_dashboard.html",

        active_page="dashboard",

        total_products=total_products,

        total_orders=total_orders,

        pending_orders=pending_orders,

        total_revenue=total_revenue,

        recent_orders=recent_orders

    )

@app.route("/vendor/add-product", methods=["GET", "POST"])
def vendor_add_product():

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        brand = request.form["brand"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]

        image = request.files["image"]

        filename = ""

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    "products",
                    filename
                )
            )

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO products(

            vendor_id,
            product_name,
            category,
            brand,
            price,
            stock,
            description,
            image,
            status

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """, (

            session["vendor_id"],
            product_name,
            category,
            brand,
            price,
            stock,
            description,
            filename,
            "Pending"

        ))

        conn.commit()

        conn.close()

        flash("Product submitted successfully. Waiting for Admin Approval.", "vendor_success")

        return redirect("/vendor/products")

    return render_template(

        "vendor_add_product.html",

        active_page="add_product"

    )

@app.route("/vendor/my-products")
def vendor_products():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM products

        WHERE vendor_id=?

        ORDER BY id DESC

    """, (session["vendor_id"],))

    products = cursor.fetchall()

    conn.close()

    return render_template(

        "vendor_my_products.html",

        products=products,

        active_page="products"

    )

@app.route("/vendor/edit-product/<int:product_id>", methods=["GET", "POST"])
def vendor_edit_product(product_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        brand = request.form["brand"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        description = request.form["description"]

        image = request.files["image"]

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    "products",
                    filename
                )
            )

            cursor.execute("""

            UPDATE products

            SET

                product_name=?,
                category=?,
                brand=?,
                price=?,
                stock=?,
                description=?,
                image=?,
                status='Pending'

            WHERE id=?
            AND vendor_id=?

            """,(

                product_name,
                category,
                brand,
                price,
                stock,
                description,
                filename,
                product_id,
                session["vendor_id"]

            ))

        else:

            cursor.execute("""

            UPDATE products

            SET

                product_name=?,
                category=?,
                brand=?,
                price=?,
                stock=?,
                description=?,
                status='Pending'

            WHERE id=?
            AND vendor_id=?

            """,(

                product_name,
                category,
                brand,
                price,
                stock,
                description,
                product_id,
                session["vendor_id"]

            ))

        conn.commit()

        flash("Product Updated Successfully.", "vendor_success")

        return redirect("/vendor/products")

    cursor.execute("""

    SELECT *

    FROM products

    WHERE id=?
    AND vendor_id=?

    """,(product_id,session["vendor_id"]))

    product = cursor.fetchone()

    conn.close()

    return render_template(

        "vendor_edit_product.html",

        product=product

    )

@app.route("/vendor/delete-product/<int:product_id>")
def vendor_delete_product(product_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT image
        FROM products
        WHERE id=?
        AND vendor_id=?
    """, (product_id, session["vendor_id"]))

    product = cursor.fetchone()

    if not product:

        conn.close()

        flash("Product not found.", "vendor_danger")

        return redirect("/vendor/products")

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "products",
        product["image"]
    )

    if os.path.exists(image_path):

        os.remove(image_path)

    cursor.execute("""
        DELETE FROM products
        WHERE id=?
        AND vendor_id=?
    """, (product_id, session["vendor_id"]))

    conn.commit()

    conn.close()

    flash("Product Deleted Successfully.", "vendor_success")

    return redirect("/vendor/products")

@app.route("/vendor/orders")
def vendor_orders():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        orders.*,

        products.product_name,

        products.image

    FROM orders

    JOIN products

    ON orders.product_id = products.id

    WHERE products.vendor_id = ?

    ORDER BY orders.id DESC

    """, (session["vendor_id"],))

    orders = cursor.fetchall()

    conn.close()

    return render_template(

        "vendor_orders.html",

        orders=orders,

        active_page="orders"
    )

@app.route("/vendor/order/<int:order_id>")
def vendor_view_order(order_id):

    if "vendor_id" not in session:

        flash("Please login first.", "vendor_warning")

        return redirect("/vendor/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        orders.*,

        products.product_name,

        products.image,

        products.vendor_id

    FROM orders

    JOIN products

    ON orders.product_id = products.id

    WHERE orders.id=?

    AND products.vendor_id=?

    """,(order_id,session["vendor_id"]))

    order = cursor.fetchone()

    conn.close()

    if order is None:

        flash("Order not found.","vendor_danger")

        return redirect("/vendor/orders")

    return render_template(

        "vendor_view_order.html",

        order=order,

        active_page="orders"

    )

@app.route("/vendor/update-status/<int:order_id>", methods=["GET", "POST"])
def vendor_update_status(order_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        orders.*,
        products.vendor_id

    FROM orders

    JOIN products

    ON orders.product_id = products.id

    WHERE orders.id=?
    AND products.vendor_id=?

    """, (order_id, session["vendor_id"]))

    order = cursor.fetchone()

    if order is None:

        conn.close()

        flash("Order not found.", "vendor_danger")

        return redirect("/vendor/orders")

    if request.method == "POST":

        status = request.form["status"]

        cursor.execute("""

        UPDATE orders

        SET status=?

        WHERE id=?

        """, (status, order_id))

        conn.commit()

        conn.close()

        flash("Order Status Updated Successfully.", "vendor_success")

        return redirect("/vendor/orders")

    conn.close()

    return render_template(
        "vendor_update_status.html",
        order=order,
        active_page="orders"
    )

@app.route("/vendor/earnings")
def vendor_earnings():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    vendor_id = session["vendor_id"]

    # Total Revenue
    cursor.execute("""
        SELECT IFNULL(SUM(orders.total_amount),0) AS total_revenue
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
        AND orders.status='Delivered'
    """, (vendor_id,))
    total_revenue = cursor.fetchone()["total_revenue"]

    # Total Orders
    cursor.execute("""
        SELECT COUNT(*) AS total_orders
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
    """, (vendor_id,))
    total_orders = cursor.fetchone()["total_orders"]

    # Delivered Orders
    cursor.execute("""
        SELECT COUNT(*) AS delivered_orders
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
        AND orders.status='Delivered'
    """, (vendor_id,))
    delivered_orders = cursor.fetchone()["delivered_orders"]

    # Pending Orders
    cursor.execute("""
        SELECT COUNT(*) AS pending_orders
        FROM orders
        JOIN products
        ON orders.product_id = products.id
        WHERE products.vendor_id=?
        AND orders.status!='Delivered'
    """, (vendor_id,))
    pending_orders = cursor.fetchone()["pending_orders"]

    # Recent Earnings
    cursor.execute("""
        SELECT
            orders.id,
            products.product_name,
            orders.total_amount,
            orders.order_date,
            orders.status
        FROM orders
        JOIN products
        ON orders.product_id=products.id
        WHERE products.vendor_id=?
        ORDER BY orders.id DESC
        LIMIT 10
    """, (vendor_id,))
    earnings = cursor.fetchall()

    conn.close()

    return render_template(
        "vendor_earnings.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        delivered_orders=delivered_orders,
        pending_orders=pending_orders,
        earnings=earnings,
        active_page="earnings"
    )

@app.route("/vendor/reports")
def vendor_reports():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    vendor_id = session["vendor_id"]

    # Total Sales

    cursor.execute("""

        SELECT
            COUNT(*) total_sales,
            IFNULL(SUM(total_amount),0) total_revenue

        FROM orders

        JOIN products
        ON orders.product_id=products.id

        WHERE products.vendor_id=?
        AND orders.status='Delivered'

    """,(vendor_id,))

    summary=cursor.fetchone()


    # Product Wise Report

    cursor.execute("""

        SELECT

            products.product_name,

            COUNT(orders.id) total_orders,

            IFNULL(SUM(orders.total_amount),0) revenue

        FROM products

        LEFT JOIN orders

        ON products.id=orders.product_id

        WHERE products.vendor_id=?

        GROUP BY products.id

        ORDER BY revenue DESC

    """,(vendor_id,))

    reports=cursor.fetchall()

    conn.close()

    return render_template(

        "vendor_reports.html",

        summary=summary,

        reports=reports,

        active_page="reports"

    )

@app.route("/vendor/profile/edit", methods=["GET", "POST"])
def edit_vendor_profile():

    if "vendor_id" not in session:
        flash("Please log in first.", "vendor_danger")
        return redirect("/vendor/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    if request.method == "POST":

        store_name = request.form.get("store_name", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        email = request.form.get("email", "").strip()
        mobile = request.form.get("mobile", "").strip()
        gst_number = request.form.get("gst_number", "").strip()
        address = request.form.get("address", "").strip()

        existing_vendor = cursor.execute(
            "SELECT logo FROM vendors WHERE id=?",
            (session["vendor_id"],)
        ).fetchone()

        logo = request.files.get("logo")
        filename = existing_vendor["logo"] if existing_vendor and existing_vendor["logo"] else ""

        if logo and logo.filename != "":
            filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config["VENDOR_UPLOAD_FOLDER"], filename))

        cursor.execute("""
            UPDATE vendors
            SET store_name=?,
                owner_name=?,
                email=?,
                mobile=?,
                gst_number=?,
                address=?,
                logo=?
            WHERE id=?
        """, (
            store_name,
            owner_name,
            email,
            mobile,
            gst_number,
            address,
            filename,
            session["vendor_id"]
        ))

        conn.commit()
        conn.close()

        session["vendor_name"] = store_name

        flash("Vendor profile updated successfully.", "vendor_success")
        return redirect("/vendor/profile")

    cursor.execute("""
        SELECT *
        FROM vendors
        WHERE id=?
    """, (session["vendor_id"],))

    vendor = cursor.fetchone()
    conn.close()

    return render_template(
        "edit_vendor_profile.html",
        vendor=vendor,
        active_page="profile"
    )

@app.route("/vendor/profile")
def vendor_profile():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM vendors
        WHERE id=?
    """, (session["vendor_id"],))

    vendor = cursor.fetchone()

    conn.close()

    return render_template(
        "vendor_profile.html",
        vendor=vendor,
        active_page="profile"
    )

@app.route("/vendor/settings")
def vendor_settings():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM vendors

        WHERE id=?

    """,(session["vendor_id"],))

    vendor=cursor.fetchone()

    conn.close()

    return render_template(

        "vendor_settings.html",

        vendor=vendor,

        active_page="settings"

    )

@app.route("/vendor/logout")
def vendor_logout():

    session.pop("vendor_id", None)
    session.pop("vendor_name", None)

    flash(
        "Logged out successfully.",
        "vendor_success"
    )

    return redirect("/vendor/login")

if __name__ == '__main__':
    app.run(debug=True)

