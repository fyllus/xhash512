#!/usr/bin/env python3
"""
xhash architecture validation and benchmarking tool.
"""

import os
import sys
import time
import xhash


def integrity16bit() -> str:
    """Exhausts the entire 16-bit space (0 to 65535) to verify structural uniqueness."""
    hashes = set()
    print("[*] Running full 16-bit space exhaustion (65536 iterations)...")

    for i in range(65536):
        data = i.to_bytes(2, 'big')
        h = xhash.xhash512(data)

        if h in hashes:
            return f"FAIL at {i} ({data.hex()})"
        hashes.add(h)

    return "CERTIFIED: 100% Unique Mapping"


def random_collision(count: int = 100_000, size: int = 64):
    """Tests collision resistance using unique sequential blocks with random padding.

    Args:
        count (int): Number of samples to test.
        size (int): Custom output digest size in bytes (e.g., 8 for xhash64, 7 for 56-bit).
    """
    hashes = set()
    start_time = time.time()
    print(f"[*] Start testing {count} samples with target output size: {size} bytes...")

    try:
        while len(hashes) != count:
            data = (len(hashes) + 1).to_bytes(4, 'big') + os.urandom(16)
            h = xhash.xhash_dyna(data, size=size)

            if h in hashes:
                print(f"\n[!] COLLISION at sample {h}")
                print(f"Input: {data.hex()}")
                break

            hashes.add(h)

            if len(hashes) % 20000 == 0:
                elapsed = time.time() - start_time
                print(f"[>] {len(hashes)} samples tested | Time: {elapsed:.2f}s")

        finished_at = (time.time() - start_time) / 60
        perc = len(hashes) / count
        tag = '[SUCCESS]' if perc == 1.0 else '[FAIL]'
        message = f"{tag}: {(1.0 - perc)*100:.2f}% of collisions in {count}, and {len(hashes)} unique samples"

        print(f"\n{'-'*60}")
        print(message)
        print(f"Total time: {finished_at:.2f} minutes")
        print(f"{'-'*60}")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")


def file_collision(filename: str):
    """Digests unique lines from a source file and tracks collision occurrence."""
    if not os.path.exists(filename):
        print(f"[-] File {filename} not found.")
        sys.exit(1)

    try:
        with open(filename, 'rb') as f:
            lines = list(set(f.readlines()))

        print(f"{'Line':<5} | {'Size':<10} | {'xhash512 Hash'}")
        print("-" * 80)

        total_start = time.time()
        hashes_seen = set()

        for idx, line in enumerate(lines, 1):
            hash_result = xhash.xhash512(line)

            if hash_result in hashes_seen:
                fail_rate = round((1.0 - (len(hashes_seen) / idx)) * 100, 2)
                print(f"\n[!] COLLISION AT LINE {idx} | Rate: {fail_rate}%")
                break

            hashes_seen.add(hash_result)
            print(f"{idx:<5} | {len(line):<8} bytes | {hash_result}")

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


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print("Usage: python test.py [16bit | random [count] [size_bytes] | file [path]]")
        sys.exit(0)

    match args[0]:
        case '16bit':
            print(integrity16bit())
        case 'random':
            target_count = int(args[1]) if len(args) > 1 else 100_000
            target_size = int(args[2]) if len(args) > 2 else 64
            random_collision(target_count, target_size)
        case 'file':
            if len(args) < 2:
                print("[-] Error: File path required.")
                sys.exit(1)
            file_collision(args[1])
        case _:
            print("[-] Unknown command.")