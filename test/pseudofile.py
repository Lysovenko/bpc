"""Simulate I/O operations"""

from time import sleep
BYTES_PER_SECOND = 1024*1024
import builtins


def open(name, mode='r'):
    if mode == 'r':
        print('real open for reading:', name)
        return builtins.open(name)
    return Pseudofile()


class Pseudofile:
    def __init__(self):
        self.bps = BYTES_PER_SECOND
        self.data = b'blah blah'

    def read(self, at_most=None):
        if at_most is not None:
            sleep(at_most / self.bps)
            return b'\0' * at_most
        return self.data

    def write(self, data):
        sleep(len(data) / self.bps)

    def __enter__(self):
        return(self)

    def __exit__(self, type, value, traceback):
        return
