import os
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL
import bcrypt
import jwt
import datetime
import json

app = Flask(__name__)

# Database configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "car_dealership"
app.config["SECRET_KEY"] = "your_secret_key"

mysql = MySQL(app)

# Error handler
def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

# Token validation
def validate_token():
    token = request.headers.get("x-access-token")

    if not token:
        return None, handle_error("Token is missing!", 401)

    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = {"user_id": data["user_id"], "role": data["role"]}
        return current_user, None
    except Exception:
        return None, handle_error("Token is invalid!", 401)

# Role validation
def validate_role(current_user, valid_roles):
    if isinstance(valid_roles, str):
        valid_roles = [valid_roles]
    
    if current_user["role"] not in valid_roles:
        return jsonify({"error": "Unauthorized access"}), 403
    return None

# users.json
users_data = {
    "users": []
}

def save_to_json():
    with open("users.json", "w") as f:
        json.dump(users_data, f)

def load_from_json():
    global users_data
    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except FileNotFoundError:
        save_to_json() 

# User registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("role"):
        return handle_error("Missing required fields: username, password, and role are mandatory", 400)

    username = data["username"]
    password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    role = data["role"]

    load_from_json()

    for user in users_data["users"]:
        if user["username"] == username:
            return handle_error("Username already exists", 400)

    new_user = {"username": username, "password": password, "role": role}
    users_data["users"].append(new_user)
    save_to_json()

    return jsonify({"message": "User registered successfully"}), 201

# User login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return handle_error("Missing required fields: username and password are mandatory", 400)

    username = data["username"]
    password = data["password"]

    load_from_json()

    for user in users_data["users"]:
        if user["username"] == username and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            token = jwt.encode(
                {
                    "user_id": username,
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify({"token": token}), 200

    return handle_error("Invalid credentials", 401)

# Error handler
def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Car Dealership API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(to right, #4e54c8, #8f94fb);
                color: #fff;
                text-align: center;
            }
            header {
                padding: 20px;
                background: #4e54c8;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            header h1 {
                margin: 0;
                font-size: 2.5rem;
            }
            main {
                padding: 20px;
            }
            main h2 {
                margin: 20px 0;
            }
            nav ul {
                list-style: none;
                padding: 0;
            }
            nav ul li {
                margin: 10px 0;
            }
            nav ul li a {
                color: #fff;
                text-decoration: none;
                font-weight: bold;
                border: 2px solid #fff;
                padding: 10px 20px;
                border-radius: 5px;
                transition: background 0.3s;
            }
            nav ul li a:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Welcome to the Car Dealership Database API</h1>
        </header>
        <main>
            <h2>Available Endpoints</h2>
            <nav>
                <ul>
                    <li><a href="/manufacturers">Manufacturers</a></li>
                    <br>
                    <br>
                    <li><a href="/branches">Branches</a></li>
                     <br>
                    <br>
                    <li><a href="/vehicles">Vehicles</a></li>
                     <br>
                    <br>
                    <li><a href="/inventory">Inventory</a></li>
                </ul>
            </nav>
            <p>Explore the available data and interact with the API.</p>
        </main>
    </body>
    </html>
    """



# Routes for retrieving data
@app.route("/manufacturers")
def get_manufacturers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Car_Manufacturers")
    manufacturers = cursor.fetchall()

    if not manufacturers:
        return handle_error("No manufacturers found", 404)

    manufacturers_list = [
        {
            "manufacturer_ID": m[0],
            "manufacturer_ShortName": m[1],
            "manufacturer_FullName": m[2],
            "manufacturer_OtherDetails": m[3],
        }
        for m in manufacturers
    ]
    return jsonify(manufacturers_list), 200

@app.route("/branches")
def get_branches():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Branches")
    branches = cursor.fetchall()

    if not branches:
        return handle_error("No branches found", 404)

    branches_list = [
        {
            "branch_location": b[0],
            "branch_other_details": b[1],
            "branch_Manager_Code": b[2],
        }
        for b in branches
    ]
    return jsonify(branches_list), 200

@app.route("/vehicles")
def get_vehicles():
    current_user, error = validate_token()
    if error:
        return error

    role_error = validate_role(current_user, ["admin", "manager"])
    if role_error:
        return role_error

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Vehicles")
    vehicles = cursor.fetchall()

    if not vehicles:
        return handle_error("No vehicles found", 404)

    vehicles_list = [
        {
            "vehicle_ID": v[0],
            "manufacturer_ID": v[1],
            "vehicle_Description": v[2],
            "vehicle_OtherDetails": v[3],
        }
        for v in vehicles
    ]
    return jsonify(vehicles_list), 200

@app.route("/inventory")
def get_inventory():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Inventory")
    inventory = cursor.fetchall()

    if not inventory:
        return handle_error("No inventory found", 404)

    inventory_list = [
        {
            "inventory_ID": i[0],
            "branch_location": i[1],
            "vehicle_ID": i[2],
            "inventory_Count": i[3],
        }
        for i in inventory
    ]
    return jsonify(inventory_list), 200

# Routes for adding data
@app.route("/manufacturers", methods=["POST"])
def add_manufacturer():

    current_user, error = validate_token()
    if error:
        return error
    role_error = validate_role(current_user, ["admin", "manager"])
    if role_error:
        return role_error





    data = request.get_json()

    if not data or not data.get("manufacturer_ShortName") or not data.get("manufacturer_FullName"):
        return handle_error("Missing required fields: manufacturer_ShortName and manufacturer_FullName", 400)

    manufacturer_ShortName = data["manufacturer_ShortName"]
    manufacturer_FullName = data["manufacturer_FullName"]
    manufacturer_OtherDetails = data.get("manufacturer_OtherDetails", None)

    try:
        cursor = mysql.connection.cursor()
        query = """
        INSERT INTO Car_Manufacturers (manufacturer_ShortName, manufacturer_FullName, manufacturer_OtherDetails)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (manufacturer_ShortName, manufacturer_FullName, manufacturer_OtherDetails))
        mysql.connection.commit()

        return jsonify({"message": "Manufacturer added successfully"}), 201
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

# PUT and DELETE methods for manufacturer
@app.route("/manufacturers/<int:manufacturer_ID>", methods=["PUT"])
def update_manufacturer(manufacturer_ID):
    data = request.get_json()

    if not data or not data.get("manufacturer_ShortName") or not data.get("manufacturer_FullName"):
        return handle_error("Missing required fields: manufacturer_ShortName and manufacturer_FullName", 400)

    manufacturer_ShortName = data["manufacturer_ShortName"]
    manufacturer_FullName = data["manufacturer_FullName"]
    manufacturer_OtherDetails = data.get("manufacturer_OtherDetails", None)

    try:
        cursor = mysql.connection.cursor()
        query = """
        UPDATE Car_Manufacturers
        SET manufacturer_ShortName = %s, manufacturer_FullName = %s, manufacturer_OtherDetails = %s
        WHERE manufacturer_ID = %s
        """
        cursor.execute(query, (manufacturer_ShortName, manufacturer_FullName, manufacturer_OtherDetails, manufacturer_ID))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Manufacturer with ID {manufacturer_ID} not found", 404)

        return jsonify({"message": "Manufacturer updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/manufacturers/<int:manufacturer_ID>", methods=["DELETE"])
def delete_manufacturer(manufacturer_ID):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Car_Manufacturers WHERE manufacturer_ID = %s"
        cursor.execute(query, (manufacturer_ID,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Manufacturer with ID {manufacturer_ID} not found", 404)

        return jsonify({"message": "Manufacturer deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

# PUT and DELETE methods for branch
@app.route("/branches/<string:branch_location>", methods=["PUT"])
def update_branch(branch_location):
    data = request.get_json()

    if not data or not data.get("branch_Manager_Code"):
        return handle_error("Missing required fields: branch_Manager_Code", 400)

    branch_Manager_Code = data["branch_Manager_Code"]
    branch_other_details = data.get("branch_other_details", None)

    try:
        cursor = mysql.connection.cursor()
        query = """
        UPDATE Branches
        SET branch_other_details = %s, branch_Manager_Code = %s
        WHERE branch_location = %s
        """
        cursor.execute(query, (branch_other_details, branch_Manager_Code, branch_location))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Branch with location {branch_location} not found", 404)

        return jsonify({"message": "Branch updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/branches/<string:branch_location>", methods=["DELETE"])
def delete_branch(branch_location):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Branches WHERE branch_location = %s"
        cursor.execute(query, (branch_location,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Branch with location {branch_location} not found", 404)

        return jsonify({"message": "Branch deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

# PUT and DELETE methods for vehicle
@app.route("/vehicles/<int:vehicle_ID>", methods=["PUT"])
def update_vehicle(vehicle_ID):
    data = request.get_json()

    if not data or not data.get("vehicle_Description"):
        return handle_error("Missing required fields: vehicle_Description", 400)

    vehicle_Description = data["vehicle_Description"]
    vehicle_OtherDetails = data.get("vehicle_OtherDetails", None)

    try:
        cursor = mysql.connection.cursor()
        query = """
        UPDATE Vehicles
        SET vehicle_Description = %s, vehicle_OtherDetails = %s
        WHERE vehicle_ID = %s
        """
        cursor.execute(query, (vehicle_Description, vehicle_OtherDetails, vehicle_ID))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Vehicle with ID {vehicle_ID} not found", 404)

        return jsonify({"message": "Vehicle updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/vehicles/<int:vehicle_ID>", methods=["DELETE"])
def delete_vehicle(vehicle_ID):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Vehicles WHERE vehicle_ID = %s"
        cursor.execute(query, (vehicle_ID,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Vehicle with ID {vehicle_ID} not found", 404)

        return jsonify({"message": "Vehicle deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

# PUT and DELETE methods for inventory
@app.route("/inventory/<int:inventory_ID>", methods=["PUT"])
def update_inventory(inventory_ID):

    current_user, error = validate_token()
    if error:
        return error
    
    role_error = validate_role(current_user, ["admin", "manager"])
    if role_error:
        return role_error


    data = request.get_json()

    if not data or not data.get("inventory_Count"):
        return handle_error("Missing required fields: inventory_Count", 400)

    inventory_Count = data["inventory_Count"]

    try:
        cursor = mysql.connection.cursor()
        query = """
        UPDATE Inventory
        SET inventory_Count = %s
        WHERE inventory_ID = %s
        """
        cursor.execute(query, (inventory_Count, inventory_ID))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Inventory with ID {inventory_ID} not found", 404)

        return jsonify({"message": "Inventory updated successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@app.route("/inventory/<int:inventory_ID>", methods=["DELETE"])
def delete_inventory(inventory_ID):

    current_user, error = validate_token()
    if error:
        return error
    
    role_error = validate_role(current_user, ["admin", "manager"])
    if role_error:
        return role_error


    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Inventory WHERE inventory_ID = %s"
        cursor.execute(query, (inventory_ID,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return handle_error(f"Inventory with ID {inventory_ID} not found", 404)

        return jsonify({"message": "Inventory deleted successfully"}), 200
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

if __name__ == '__main__':
    app.run(debug=True)
