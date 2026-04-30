#!/usr/bin/env python
import os, sys

args = sys.argv[1:]

size = 0
if args[1]:
    try:
        size = int(args[1])
    except:
        print(f'[-] Put a valid int size for test file append')

with open(args[0], 'ab') as file:
    for i in range(size):
        line = os.urandom(32) + b'\n'
        file.write(line)
        print(f' Line {i} generate random line:', line)
