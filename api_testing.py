import pytest
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from api import app

# Fixture to mock database
@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

# General Tests
def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Car Dealership Database API" in response.data

# Manufacturers Table Tests
def test_get_manufacturers_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/manufacturers')
    
    assert response.status_code == 404
    assert b"No manufacturers found" in response.data

def test_get_manufacturers(mock_db):
    mock_db.fetchall.return_value = [
        (1, 'Toyota', 'Toyota Motor Corporation', 'Automobile manufacturer'),
        (2, 'Honda', 'Honda Motor Co., Ltd.', 'Automobile manufacturer')
    ]
    
    client = app.test_client()
    response = client.get('/manufacturers')
    
    assert response.status_code == 200
    assert b"Toyota" in response.data
    assert b"Honda" in response.data

def test_add_manufacturer_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/manufacturers', json={})
    
    assert response.status_code == 400
    assert b"Missing required fields: manufacturer_ShortName and manufacturer_FullName" in response.data

def test_add_manufacturer_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/manufacturers', json={
        'manufacturer_ShortName': 'Ford',
        'manufacturer_FullName': 'Ford Motor Company'
    })
    
    assert response.status_code == 201
    assert b"Manufacturer added successfully" in response.data

def test_update_manufacturer_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.put('/manufacturers/1', json={
        'manufacturer_ShortName': 'Updated Name',
        'manufacturer_FullName': 'Updated Full Name',
        'manufacturer_OtherDetails': 'Updated Details'
    })
    assert response.status_code == 200
    assert b"Manufacturer updated successfully" in response.data

def test_update_manufacturer_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.put('/manufacturers/999', json={})
    assert response.status_code == 400
    assert b"Missing required fields: manufacturer_ShortName and manufacturer_FullName" in response.data

def test_delete_manufacturer_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/manufacturers/1')
    assert response.status_code == 200
    assert b"Manufacturer deleted successfully" in response.data

def test_delete_manufacturer_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/manufacturers/999')
    assert response.status_code == 404

# Branches Table Tests
def test_get_branches_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/branches')
    
    assert response.status_code == 404
    assert b"No branches found" in response.data

def test_get_branches(mock_db):
    mock_db.fetchall.return_value = [
        ('New York', 'Downtown branch', '123'),
        ('Los Angeles', 'West Coast branch', '456')
    ]
    
    client = app.test_client()
    response = client.get('/branches')
    
    assert response.status_code == 200
    assert b"New York" in response.data
    assert b"Los Angeles" in response.data

# Vehicles Table Tests
def test_get_vehicles_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/vehicles')
    
    assert response.status_code == 404
    assert b"No vehicles found" in response.data

def test_get_vehicles(mock_db):
    mock_db.fetchall.return_value = [
        (1, 1, 'SUV Model', 'Electric vehicle')
    ]
    
    client = app.test_client()
    response = client.get('/vehicles')
    
    assert response.status_code == 200
    assert b"SUV Model" in response.data

# Inventory Table Tests
def test_get_inventory_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/inventory')
    
    assert response.status_code == 404
    assert b"No inventory found" in response.data

def test_get_inventory(mock_db):
    mock_db.fetchall.return_value = [
        (1, 'New York', 1, 5)
    ]
    
    client = app.test_client()
    response = client.get('/inventory')
    
    assert response.status_code == 200
    assert b"New York" in response.data
