""" this is to test my FastAPI route which must be up and running 
    see the docstring in the fastapi_cache.py source
    
    To start the locust load test use:
    poetry run locust -f locust_test.py from the directory in which you have the locust_test-py file
    
    Go the the http://localhost:8089 and in the starting panel you need to fill up all three fields:
    1) Maximum number of concurrent users
    2) How many seconds to wait before ramping up to the next concurrent user
    3) The endpoint address. 
    In our case it will be http://127.0.0.1:8000 since our FastAPI server 
    will be running under uvicorn there
"""
import random
import string

from locust import HttpUser, between, task


def generate_random_permutation():
    """generate a random 3 nonrepeating letters string to test our endpoint (15K permutations)"""
    letters = string.ascii_lowercase
    return "".join(random.sample(letters, 3))


class PerformanceTests(HttpUser):
    """our Locust class"""

    wait_time = between(1, 3)

    @task(1)
    def cache_test(self):
        """our first (and only) test case"""
        random_string = generate_random_permutation()
        response = self.client.get(f"/cache/{random_string}")
        print("Response status code:", response.status_code)
        print("Response JSON:", response.json())
