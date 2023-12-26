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
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()


def url_access_count(method: Callable) -> Callable:
    """Decorator for get_page function"""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function"""
        key = "cached:" + url
        cached_value = redis_store.get(key)

        if cached_value:
            return cached_value.decode("utf-8") if cached_value else ""

        # Get new content and update cache
        key_count = "count:" + url
        html_content = method(url)

        redis_store.incr(key_count)
        redis_store.set(key, html_content, ex=10)
        redis_store.expire(key, 10)

        return html_content
    return wrapper


@url_access_count
def get_page(url: str) -> str:
    """Obtain the HTML content of a particular URL"""
    results = requests.get(url)
    return results.text

