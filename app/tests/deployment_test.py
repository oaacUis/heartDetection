import asyncio
import httpx
import time
from client import get_jwt_token
import json


# URL = "http://127.0.0.1:8000"
base_url = "http://192.168.73.37:5000"
# predict_url = "http://127.0.0.1:5001"
predict_url = "http://192.168.73.37:5001"

auth_data = {"username": "CPS_OTTO_ANDRADE_DEV", "password": "UIS@123"}
with open("input_test.json") as f:
    data = json.load(f)
token = get_jwt_token(base_url + "/auth/token", auth_data)
# headers = {"Authorization": f"Bearer {token}"}
headers = {"token": token}


async def send_request(client, data, headers, timeout):
    try:
        response = await client.post(predict_url + "/models", json=data,
                                     headers=headers, timeout=timeout)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)


async def main(num_requests, data, headers, timeout):
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, data, headers, timeout) for _ in range(num_requests)]
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        success_responses = [r for r in responses if r[0] == 200]
        failed_responses = [r for r in responses if r[0] is None or r[0] != 200]
        all_responses = [r for r in responses]

        print("All responses:", all_responses)
        print(f"Total requests: {num_requests}")
        print(f"Successful responses: {len(success_responses)}")
        print(f"Failed responses: {len(failed_responses)}")
        print(f"Total time taken: {end_time - start_time} seconds")


num_requests = 500
timeout = 30  # seconds
asyncio.run(main(num_requests, data, headers, timeout))
