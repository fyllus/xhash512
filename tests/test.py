#!/usr/bin/env python3
from xhash512 import xh512
import time
import sys

if __name__ == '__main__':

    arg = sys.argv[1:]
    if arg:
        with open(arg[0], 'r') as file:
            file = file.read()

        start = time.time()

        size = len(file.encode())

        print(f'\nFile size : {size} bytes')

        print(f"\nFile xh512: {xh512(file.encode()).decode()}")

        print(f'\nHash Time: {time.time() - start}\n')
