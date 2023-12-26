#!/usr/bin/env python3
'''
    Create a Cache class. In the __init__ method
    store an instance of the Redis client as a
    private variable named _redis (using redis.Redis())
    and flush the instance using flushdb.

    Create a store method that takes a data argument and
    returns a string. The method should generate a random
    key (e.g. using uuid), store the input data in Redis
    using the random key and return the key.

    Type-annotate store correctly. Remember that data can
    be a str, bytes, int or float.
'''
import uuid
import redis
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
        Decorator to count the number of calls to the decorated method
    '''
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # wrapper for decorated function
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    '''
        store the history of inputs and outputs
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''
            wrapper for the decorated function
        '''
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output

    return wrapper


def replay(fn: Callable):
    '''
        display the history of calls of a particular function
    '''
    r = redis.Redis()
    function_name = fn.__qualname__
    value = r.get(function_name)
    try:
        value = int(value.decode("utf-8"))
    except Exception:
        value = 0

    print("{} was called {} times:".format(function_name, value))
    inputs = r.lrange("{}:inputs".format(function_name), 0, -1)

    outputs = r.lrange("{}:outputs".format(function_name), 0, -1)

    for input, output in zip(inputs, outputs):
        try:
            input = input.decode("utf-8")
        except Exception:
            input = ""

        try:
            output = output.decode("utf-8")
        except Exception:
            output = ""

        print("{}(*{}) -> {}".format(function_name, input, output))


class Cache:
    def __init__(self):
        # Initialize Redis client and flush the database
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        # Generate a random key using uuid
        key = str(uuid.uuid4())

        # Store the data in Redis with the generated key
        self._redis.set(key, data)

        # Return the generated key
        return key

    def get(self, key: str,
            fn: Optional[callable] = None) -> Union[str, bytes, int, float]:
        # convert the data back to the desired format
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''
            automatically parametrize Cache.get with
            the correct conversion function
        '''
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        '''
            automatically parametrize Cache.get with
            the correct
            conversion function
        '''
        value = self._redis.get(key)
        try:
            value = int(value.decode("utf-8"))
        except Exception:
            value = 0
        return value
