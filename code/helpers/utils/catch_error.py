'''
 Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify,
 merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from functools import wraps
from botocore.exceptions import ClientError
from helpers.logger import logger


def catch_error(error, handler=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error as err:
                if handler:
                    return handler()
                else:
                    logger.debug(
                        'Error {} was ignored while execute function {}'.
                        format(err, func.__name__)
                    )
                    return None
        return wrapper
    return decorator


def client_error_ignore(code):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                if err.response['Error']['Code'] == code:
                    logger.debug(
                        'ClientError {} was ignored while execute function {}'.
                        format(code, func.__name__)
                    )
                    return None
                else:
                    raise err
        return wrapper
    return decorator


def client_error_handle(code, handler):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                if err.response['Error']['Code'] == code:
                    return handler(*args, **kwargs)
                else:
                    raise err
        return wrapper
    return decorator


def client_error_retry(code, resolver):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                if err.response['Error']['Code'] == code:
                    resolver(args[0])
                    return func(*args, **kwargs)
                else:
                    raise err
        return wrapper
    return decorator


def client_error_wait_and_retry(code):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                if err.response['Error']['Code'] == code:
                    return func(*args, **kwargs)
                else:
                    raise err
        return wrapper
    return decorator
