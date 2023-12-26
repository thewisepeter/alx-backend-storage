#!/usr/bin/env python3
'''
    In this tasks, we will implement a get_page
    function (prototype: def get_page(url: str) -> str:).
    The core of the function is very simple. It uses the
    requests module to obtain the HTML content of a particular
    URL and returns it.

    Start in a new file named web.py and do not reuse the code
    written in exercise.py.

    Inside get_page track how many times a particular URL was
    accessed in the key "count:{url}" and cache the result with
    an expiration time of 10 seconds.

    Tip: Use http://slowwly.robertomurray.co.uk to simulate a
    slow response and test your caching.

    Bonus: implement this use case with decorators.
'''

import requests
import redis
from functools import wraps
import time

# Redis instance
redis_client = redis.Redis()

def count_calls(func):
    @wraps(func)
    def wrapper(url):
        # Increment the count for the accessed URL
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return func(url)
    return wrapper

def cache_result(duration=10):
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            result_key = f"result:{url}"
            cached_result = redis_client.get(result_key)

            if cached_result:
                return cached_result.decode("utf-8")
            else:
                result = func(url)
                redis_client.setex(result_key, duration, result)
                return result
        return wrapper
    return decorator

@count_calls
@cache_result()
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

# Example usage:
if __name__ == "__main__":
    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"

    # Access slow URL multiple times
    for _ in range(3):
        html_content = get_page(slow_url)
        print(html_content)

    # Access a fast URL
    fast_url = "http://www.example.com"
    html_content = get_page(fast_url)
    print(html_content)

    # Print the count for the slow URL
    slow_url_count = redis_client.get(f"count:{slow_url}")
    print(f"The slow URL was accessed {slow_url_count} times.")
