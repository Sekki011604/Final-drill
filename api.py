import os
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "car_Dealership"

mysql = MySQL(app)

# Error handler
def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return "Welcome to the Car Dealership Database API"


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

# Example: More POST, PUT, DELETE routes for `branches`, `vehicles`, `inventory` as required.

if __name__ == '__main__':
    app.run(debug=True)
