import requests
import json

# Base URL of the local app
base_url = "http://127.0.0.1:5000"
predict_url = "http://127.0.0.1:5001"

# Load the input data for the predict endpoint
with open('input_test.json') as f:
    input_data = json.load(f)
print(type(input_data))

# Authentication credentials
auth_data = {
    "username": "CPS_DAVID_PEREZ_DEV",
    "password": "UIS@123FCV"
}


def get_jwt_token(auth_url, auth_data):
    try:
        response = requests.post(auth_url, data=auth_data)
        print(response.json().get('access_token'))
        return response.json().get('access_token')
    except Exception as e:
        print(e)
        print("Could not get JWT token")
        return None


# Endpoints
endpoints = {
    "login": "/",
    "predict": "/predict"
}

# Test each endpoint
# Get JWT token
token = get_jwt_token(base_url + "/auth/token", auth_data)
headers = {'token': token}
print("headers:", headers), print()

print(), print("Checking the health of the predict service...")
response_check = requests.get(predict_url + "/")
print(response_check.json())
print("="*50)

print(), print("Checking the health of the main service...")
response_check = requests.get(base_url + "/home")
print(response_check.json())
print("="*50)

# response = requests.post(base_url + "/predict",
#                          json=input_data, headers=headers)

response = requests.post(predict_url + "/models",
                         json=input_data, headers=headers)


print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
print("="*50)

response_validate_user = requests.get(base_url + "/", json=headers)
print(f"Active User is: {response_validate_user.json()}")
print("="*50)
