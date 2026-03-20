import requests
import json

# Test register
print("Testing register...")
data = {
    "username": "testuser2",
    "email": "test2@email.com", 
    "password": "123456"
}

try:
    response = requests.post('http://localhost:5000/api/auth/register', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test login
print("\nTesting login...")
data = {
    "email": "test2@email.com",
    "password": "123456"
}

try:
    response = requests.post('http://localhost:5000/api/auth/login', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
