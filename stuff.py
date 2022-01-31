import time


def loop(count):
    def decorator(func):
        for i in range(count):
            func(i)
    return decorator


def stopwatch(func):
    def inner(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print(f"{func} took: {time.time() - start} seconds to execute")
        return res
    return inner
