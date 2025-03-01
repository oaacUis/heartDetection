import requests  # type: ignore
import json
from dotenv import load_dotenv
import os
load_dotenv()

# Base URL of the local app
base_url = "http://127.0.0.1:5000"
predict_url = "http://127.0.0.1:8000"

# Load the input data for the predict endpoint
with open('input_test.json') as f:
    input_data = json.load(f)
print(type(input_data))

# Authentication credentials
auth_data = {
    "username": "CPS_DAVID_PEREZ_DEV",
    "password": "UIS@123FCV"
}

# Endpoints
endpoints = {
    "login": "/",
    "predict": "/models"
}

token = os.getenv("API_KEY")
headers = {'token': token}
print("headers:", headers), print()

print(), print("Checking the health of the predict service...")
response_check = requests.get(predict_url + "/")
print(response_check.json())
print("="*50)


# response = requests.post(base_url + "/predict",
#                          json=input_data, headers=headers)

response = requests.post(predict_url + "/models",
                         json=input_data, headers=headers)


print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
print("="*50)

