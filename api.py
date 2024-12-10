import os
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "car_dealership"

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
