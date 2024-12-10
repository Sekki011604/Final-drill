# Car Dealership Database API

## Description
A Flask-based REST API for managing car manufacturers, branches, vehicles, and inventory in a car dealership database.

## Installation
To install the required dependencies for the project, run:
```bash
pip install -r requirements.txt
```
## Configuration
To configure the database:
1. Upload the ```car_dealership``` database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password (password of your local host)
- ```MYSQL_DB```: Name of the database (e.g., car_dealership)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Welcome message |
| /manufacturers	| GET	| 	List all manufacturers |
| /manufacturers	| POST	|Add a new manufacturer |
| /manufacturers/<id>	| PUT	| Update manufacturer details |
| /manufacturers/<id>	| DELETE	|Delete a manufacturer |
| /branches	| GET	| List all branches |
| /branches	| POST	| Add a new branch |
| /branches/<id>	| PUT	| Update branch details |
| /branches/<id>	| DELETE	| Delete a branch |
| /vehicles	| GET	| List all vehicles |
| /vehicles	| POST	| Add a new vehicle |
| /vehicles/<id>	| PUT	| Update vehicle details |
| /vehicles/<id>	| DELETE	| Delete a vehicle |
| /inventory	| GET	| List all inventory items |
| /inventory	| POST	| Add new inventory items |
| /inventory/<id>	| PUT	| Update inventory item details |
| /inventory/<id>		| DELETE	| Delete inventory item |

## Testing
To run the tests, follow these steps:
1. Ensure you have ```pytest``` and ```pytest-mock``` installed. You can install them with:
```bash
pip install pytest pytest-mock
```
2. Run the tests by executing the following command:
```bash
pytest api_test.py
```

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests
```


### Conclusion
This is the complete set of code for the Car Dealership API, including all database table structures, the Flask app logic, and the `README.md` documentation. You can use the above SQL commands to set up your database tables and run the API in your local development environment.

Let me know if you need further assistance!
