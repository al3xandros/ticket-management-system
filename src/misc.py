import re

class IDFactory:
    def __init__(self):
        self.i = 0

    def __call__(self):
        j = self.i
        self.i += 1
        return j
