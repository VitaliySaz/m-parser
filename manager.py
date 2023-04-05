import datetime
import time

future = None
def time_manager(timedelta):
    def wrapper(func):
        def decorate(*args, **kwargs):
            global future
            td = datetime.timedelta(**timedelta)
            now = datetime.datetime.now()
            if not future:
                future = now + td
            remaining_seconds = (future - now).total_seconds()
            if remaining_seconds < 0:
                func(*args, **kwargs)
                future = now + td
        return decorate
    return wrapper


class Manager:

    def __init__(self):
        self.base_compare = set()
        self.new_compare = set()

    @property
    def difference(self):
        if not self.base_compare:
            return self.new_compare
        return self.new_compare - self.base_compare

    def add_comparison(self, comparison):
        self.base_compare.update(self.new_compare)
        self.new_compare = set(comparison)

    def to_reset(self):
        self.base_compare = set()

if __name__ == '__main__':

    def g():
        print('hello')

    for _ in range(100):
        print('as')
        time_manager({'seconds': 5})(g)()
        time.sleep(1)
