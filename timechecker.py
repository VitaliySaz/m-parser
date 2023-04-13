import datetime


class CallAfterTimedeltaError(Exception):
    pass


class OtherTimeError(Exception):
    pass


class TimeChecker:

    @staticmethod
    def call_after_delta(**time):
        future = None

        def decorator(func):
            def wrapper(*args, **kwargs):
                nonlocal future
                td = datetime.timedelta(**time)
                now = datetime.datetime.now()
                if not future:
                    future = now + td
                remaining_seconds = (future - now).total_seconds()
                if remaining_seconds < 0:
                    future = now + td
                    return func(*args, **kwargs)
                raise OtherTimeError(
                    f"Function {func.__name__} can only be called after {remaining_seconds} sec.")

            return wrapper

        return decorator

    @staticmethod
    def call_within_timeframe(start_time, end_time):
        def decorator(func):
            def wrapper(*args, **kwargs):
                now = datetime.datetime.now().time()
                if datetime.time(*start_time) <= now <= datetime.time(*end_time):
                    return func(*args, **kwargs)
                raise CallAfterTimedeltaError(
                    f"Function {func.__name__} can only be called between {start_time} and {end_time}.")

            return wrapper

        return decorator
