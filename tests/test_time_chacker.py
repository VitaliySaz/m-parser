import time
import unittest
import datetime

from timechecker import TimeChecker, CallAfterTimedeltaError, OtherTimeError


class TestTimeChecker(unittest.TestCase):

    def test_call_after_delta(self):
        tc = TimeChecker()

        @tc.call_after_delta(seconds=1)
        def my_func():
            return "Hello"

        # First  call should fail with OtherTimeError
        with self.assertRaises(OtherTimeError):
            my_func()

        time.sleep(1.2)

        # Second call should succeed
        result = my_func()
        self.assertEqual(result, "Hello")

    def test_call_within_timeframe(self):
        tc = TimeChecker()

        start_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        end_time = datetime.datetime.now() - datetime.timedelta(hours=1)

        @tc.call_within_timeframe((start_time.hour,), (end_time.hour,))
        def my_func():
            return "Hello"

        # Call before the time frame should fail with CallAfterTimedeltaError
        with self.assertRaises(CallAfterTimedeltaError):
            my_func()

        start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        end_time = datetime.datetime.now() + datetime.timedelta(hours=1)

        @tc.call_within_timeframe((start_time.hour,), (end_time.hour,))
        def my_func():
            return "Hello"
