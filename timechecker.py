import datetime


class CallAfterTimedeltaError(Exception):
    pass


class OtherTimeError(Exception):
    pass


class TimeChecker:

    def __init__(self):
        self.future = None

    def call_after_delta(self, timedelta_limit):
        def decorator(func):
            def wrapper(*args, **kwargs):
                td = datetime.timedelta(**timedelta_limit)
                now = datetime.datetime.now()
                if not self.future:
                    self.future = now + td
                remaining_seconds = (self.future - now).total_seconds()
                if remaining_seconds < 0:
                    self.future = now + td
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
                if start_time <= now <= end_time:
                    return func(*args, **kwargs)
                raise CallAfterTimedeltaError(
                    f"Function {func.__name__} can only be called between {start_time} and {end_time}.")
            return wrapper
        return decorator
