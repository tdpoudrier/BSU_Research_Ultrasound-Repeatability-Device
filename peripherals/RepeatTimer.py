"""
    Author: Tevin Poudrier
    Date: Thu Jul 25 10:41:11 PM MDT 2024
    Description: A timer that repeats at the defined interval. Was copied from stack overflow 
"""

from threading import Timer
import time


class RepeatTimer(Timer):
    def run(self):
        """
        Start timer
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == "__main__":

    def dummy_function(msg='test'):
        print(msg)

    timer = RepeatTimer(1, dummy_function)
    timer.start()

    time.sleep(5)

    timer.cancel()