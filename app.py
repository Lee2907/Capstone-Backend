import hmac
import sqlite3
from datetime import datetime
import datetime
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):
    def __init__(self, user_id, first_name, last_name, username, password, user_email, phone_number, address):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address


# user tables
def user_reg():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS Users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 first_name TEXT NOT NULL,
                 last_name TEXT NOT NULL,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL,
                 address TEXT NOT NULL,
                 phone_number INT NOT NULL,
                 user_email TEXT NOT NULL)''')
    print("user table created successfully")
    conn.close()


# products table
def products():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS Products(product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_picture TEXT NOT NULL,
                 product_name TEXT NOT NULL,
                 price INTEGER NOT NULL,
                 description TEXT NOT NULL,
                 product_type TEXT NOT NULL,
                 quantity INTEGER NOT NULL,
                 order_id INTEGER NOT NULL,
                 FOREIGN KEY (order_id) REFERENCES users(user_id))''')
    print("products table created successfully")
    conn.close()


#recipient table
def recipient():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS recipient_table(recipient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 recipient_name TEXT NOT NULL,
                 recipient_lastname TEXT NOT NULL,
                 recipient_address TEXT NOT NULL,
                 city TEXT NOT NULL, 
                 province TEXT NOT NULL,
                 postal_code TEXT NOT NULL, 
                 recipient_phone TEXT NOT NUll, 
                 user_id INTEGER NOT NULL,
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    print("recipient table created successfully")
    conn.close()


# order table
def checkout_table():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS checkout_table(order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_image TEXT NOT NULL,
                 order_date TEXT NOT NULL, 
                 order_number INTEGER NOT NULL,
                 product_name TEXT NOT NULL,
                 total_price TEXT INTEGER NOT NULL,
                 product_quantity INTEGER NOT NULL,
                 FOREIGN KEY (order_number) REFERENCES users (user_id))''')
    print("orders table created successfully")
    conn.close()


def contact_us():
    conn = sqlite3.connect('products.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS contact(contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 contact_no TEXT NOT NULL,
                 email_address TEXT NOT NULL,
                 enquiry TEXT NOT NULL)''')
    print("orders table created successfully")
    conn.close()


user_reg()
products()
checkout_table()
recipient()
contact_us()


def fetch_users():
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[1], data[2], data[3], data[4], data[5], data[6],
                                 data[7]))
    return new_data


users = fetch_users()


username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# identify registered user by user id
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

# authenticate a logon in user
jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@cross_origin()
@jwt_required()
def protected():
    return '%s' % current_identity


# register a new user
@app.route('/user-registration/', methods=["POST", "GET", "PATCH"])
@cross_origin()
def user_registration():
    response = {}
    if request.method == "POST":

        #try:

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        user_email = request.form['user_email']

        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users("
                            "first_name,"
                            "last_name,"
                            "username,"
                            "password,address,phone_number,user_email) VALUES(?, ?, ?, ?, ?, ?, ?)",
                            (first_name, last_name, username, password, address, phone_number, user_email))
            conn.commit()
            response["message"] = "User registered successfully "
            response["status_code"] = 201

            return response
        #except Exception:

            #response["message"] = "Invalid user supplied"
            #response["status_code"] = 401
            #return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Users")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)
    # LOGIN
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        with sqlite3.connect("products.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", (username, password,))
            user = cursor.fetchone()
        response['status_code'] = 200
        response['data'] = user
        return response


# get single user
@app.route('/user/<int:user_id>', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_user(user_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        # cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Users WHERE user_id=" + str(user_id))
        user = cursor.fetchone()
        # accumulator = []
        # for i in user:
        # accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = user  # tuple(accumulator)
    return response


# delete user by id
@app.route("/delete-user/<int:post_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_product(post_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "User deleted successfully."
    return response


# update single user
@app.route('/update-user/<int:user_id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def edit_user(user_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('products.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("first_name") is not None:  # check if the updated column is first_name
                put_data["first_name"] = incoming_data.get("first_name")
                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET first_name =? WHERE user_id=?", (put_data["first_name"], user_id))
                    conn.commit()
                    response['message'] = "First name updated"
                    response['status_code'] = 200
            if incoming_data.get("last_name") is not None:
                put_data['last_name'] = incoming_data.get('last_name')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET last_name =? WHERE user_id=?", (put_data["last_name"], user_id))
                    conn.commit()

                    response["content"] = "Last name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("username") is not None:
                put_data['username'] = incoming_data.get('username')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET username =? WHERE user_id=?", (put_data["username"], user_id))
                    conn.commit()

                    response["content"] = "Username updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET password =? WHERE user_id=?", (put_data["password"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("address") is not None:
                put_data['address'] = incoming_data.get('address')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET address =? WHERE user_id=?", (put_data["address"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("phone_number") is not None:
                put_data['phone_number'] = incoming_data.get('phone_number')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET phone_number =? WHERE user_id=?",
                                   (put_data["phone_number"], user_id))
                    conn.commit()

                    response["content"] = "Phone number updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("user_email") is not None:
                put_data['user_email'] = incoming_data.get('user_email')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET user_email =? WHERE user_id=?", (put_data["user_email"], user_id))
                    conn.commit()

                    response["content"] = "E-mail address updated successfully"
                    response["status_code"] = 200

    return response


# View all products
@app.route('/create-products/', methods=["POST", "GET"])
@cross_origin()
def products_info():
    response = {}
    if request.method == "POST":
        try:
            picture = request.form['product_picture']
            name = request.form['product_name']
            price = request.form['price']
            desc = request.form['description']
            product_type = request.form['product_type']
            quantity = request.form['quantity']
            order_id = request.form['order_id']

            with sqlite3.connect("products.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Products(
                               product_picture,
                               product_name,
                               price,
                               description,
                               product_type,
                               quantity,
                               order_id) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (picture, name, price, desc, product_type, quantity, order_id))
                conn.commit()
                response["message"] = "Product has been added successfully "
                response["status_code"] = 200

                return response
        except Exception:
            response["message"] = "Enter the product in the correct manner"
            response["status_code"] = 404
            return response
    if request.method == "GET":

        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM Products")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# get product by id
@app.route('/single_product/<int:order_id>', methods=["GET"])
@cross_origin()
def get_product(order_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Products WHERE order_id=" + str(order_id))
        user = cursor.fetchone()
        accumulator = []
        for i in user:
            accumulator.append({k: i[k] for k in i.keys()})
    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


# update product by id
@app.route('/update-product/<int:product_id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def update_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('products.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("product_name") is not None:  # check if the updated column is price
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET product_name =? WHERE product_id=?", (put_data["product_name"], product_id))
                    conn.commit()
                    response['message'] = "Product name updated"
                    response['status_code'] = 200

            if incoming_data.get("product_picture") is not None:
                put_data['product_picture'] = incoming_data.get('product_picture')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET product_picture =? WHERE product_id=?",
                                   (put_data["product_picture"], product_id))
                    conn.commit()

                    response["content"] = "Product type updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET price =? WHERE product_id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["content"] = "Product price updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Products SET description =? WHERE product_id=?", (put_data["description"], product_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("product_type") is not None:
                put_data['product_type'] = incoming_data.get('product_type')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_type =? WHERE product_id=?",
                                   (put_data["product_type"], product_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("quantity") is not None:
                put_data['quantity'] = incoming_data.get('quantity')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET quantity =? WHERE product_id=?",
                                   (put_data["size"], product_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("order_id") is not None:
                put_data['order_id'] = incoming_data.get('order_id')

                with sqlite3.connect('products.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET order_id =? WHERE product_id=?", (put_data["order_id"], product_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

    return response


# delete product by id
@app.route("/delete-product/<int:product_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_single_product(product_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE product_id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


@app.route('/orders/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def checkout_info():
    response = {}
    now = datetime.now()
    if request.method == "POST":
        try:
            product_image = request.form['product_image']
            order_number = request.form['order_number']
            product_name = request.form['product_name']
            total_price = request.form['total_price']
            product_quantity = request.form['product_quantity']

            with sqlite3.connect("products.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO checkout_table(
                               product_image,
                               order_date,
                               order_number,
                               product_name,
                               total_price,
                               product_quantity) VALUES(?, ?, ?, ?, ?, ?)''',
                               (product_image, now, order_number, product_name, total_price, product_quantity))
                conn.commit()
                response["message"] = "Order added successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter correct order"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM checkout_table")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# get single order by id
@app.route('/single_order/<int:order_number>', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_order(order_number):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM orders WHERE order_number=" + str(order_number))
        user = cursor.fetchone()
        accumulator = []
        for i in user:
            accumulator.append({k: i[k] for k in i.keys()})
    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


# delete single order
@app.route("/delete-order/<int:order_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_order(order_id):
    response = {}
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id=" + str(order_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Order deleted successfully."
    return response


# the checkout
@app.route('/checkout/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def checkin_out():
    response = {}
    now = datetime.now()
    if request.method == "POST":
        try:

            recipient_name = request.form['recipient_name']
            recipient_lastname = request.form['recipient_lastname']
            company = request.form['company']
            recipient_address = request.form['recipient_address']
            city = request.form['city']
            postal_code = request.form['product_condition']

            with sqlite3.connect("products.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO checkout_table(
                               recipient_name,
                               recipient_lastname,
                               company,
                               recipient_address,
                               city,
                               postal_code) VALUES(?, ?, ?, ?, ?, ?)''',
                               (recipient_name, recipient_lastname, company, recipient_address, city,
                                postal_code))
                conn.commit()
                response["message"] = "Alternate address added"
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter full alternate address"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM recipient_address")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# contact section
@app.route('/contact-us/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def contact():
    response = {}
    if request.method == "POST":
        try:

            name = request.form['name']
            contact = request.form['contact_no']
            email_address = request.form['email_address']
            enquiry = request.form['enquiry']

            with sqlite3.connect("products.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO contact(
                               name,
                               contact_no,
                               email_address,
                               enquiry) VALUES(?, ?, ?)''',
                               (name, contact, email_address, enquiry))
                conn.commit()
                response["message"] = "Enquiry registered successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter valid details"
            response["status_code"] = 401
            return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM contact")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
