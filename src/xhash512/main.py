#!/usr/bin/env python3

from .xhash512 import XHash
from .xbase64 import XBase64

import time
import sys, os, argparse

def random_collision(count=100_000, mods=2):
    xhash = XHash(mods)
    hashes = set()
    start_time = time.time()
    print(f"[*] Start testing {count} samples...")
    try:
        while len(hashes) != count:
            data = (len(hashes) + 1).to_bytes(4, 'big') + os.urandom(16)
            hash = xhash.xh512(data).decode()
            if hash in hashes:
                print(f"\n[!] COLLISION at sample {hash}")
                print(f"Input: {data}")
                break
            hashes.add(hash)
            if len(hashes)%1000 == 0:
                elapsed = time.time() - start_time
                print(f"[>] {len(hashes)} samples tested | Time: {elapsed:.2f}s")
                time.sleep(0.02)

        fished_at = f"{(time.time() - start_time)/60:.2f} minutes"
        perc = len(hashes)/count
        tag = '[SUCCESS]' if perc == 1.0 else '[FAIL]'
        message = f"{tag}: {(1.0 - perc)*100:.2f} of collions in {count}, and {len(hashes)} unique samples"

        print(f"\n{'-'*60}")
        print(message)
        print(f"Total time: {fished_at}")
        print(f"{'-'*60}")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

def file_collision(filename, mods):
    xhash = XHash(mods or 2)

    if not os.path.exists(filename):
        print(f"[-] File {filename} not found.")
        sys.exit(1)

    try:
        with open(filename, 'rb') as f:
            lines = list(set(f.readlines()))

        print(f"{'Line':<5} | {'Size':<10} | {'xh512 Hash'}")
        print("-" * 80)

        total_start = time.time()
        hashes_seen = set()

        for idx, line in enumerate(lines, 1):
            if idx%100 == 0:
                time.sleep(0.01)
            clean_line = line

            hash_result = xhash.xh512(clean_line).decode()

            if hash_result in hashes_seen:
                fail_rate = round((1.0 - (len(hashes_seen) / idx)) * 100, 2)
                print(f"\n[!] COLLISION AT LINE {idx} | Rate: {fail_rate}%")
                break

            hashes_seen.add(hash_result)

            print(f"{idx:<5} | {len(clean_line):<8} bytes | {hash_result} ")

        duration = time.time() - total_start
        total_size = os.path.getsize(filename)

        print("-" * 80)
        print(f"Total processing time: {duration:.4f}s")
        print(f"\n{'='*60}")
        print(f"TARGET: {filename} | {len(lines)} unique lines")
        print(f"TOTAL SIZE: {total_size} bytes | STATUS: {'PASS' if len(hashes_seen) == len(lines) else 'FAIL'}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"[-] Error: {e}")
"""
principal:

--xbase64
--xhash512
--collision

--xbase64:
    seed (obrigartorio)
    --rng

    --seed

    --base:
        base (obrigatorio)
        steps (opicional)

--xhash512:
    --mods
    --data
--collision:
    --file:
        name
    --random


"""