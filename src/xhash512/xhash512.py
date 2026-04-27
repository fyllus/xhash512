#!/usr/bin/env python3

"""
Project : Xhash512
Author  : Fyllus(Geliardi D. Oliveira)
Version : 0.1.0
Desc    : Experimental project for 512 bits hash with dynamic base64 output
"""

import hashlib, random


SEQUENCES = [
    b'0123456789',             # 0-9
    b'abcdef',                 # a-f
    b'ghijklmnopqrstuvwxyz',   # g-z
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZ+-' # A-Z
]

def xcut_shuffle(cut: bytes, seed: bytes):
    """
    Shuffles a byte segment multiple times based on seed tokens.
    """
    temp_cut = bytearray(cut)

    for tok in seed:
        # Each byte in seed acts as a deterministic shuffler state
        shuffler = random.Random(tok)
        shuffler.shuffle(temp_cut)

    return bytes(temp_cut)

def xpack_shuffle(pack: list[bytes], seed: bytes):
    """
    Derives a high-entropy seed via PBKDF2 and shuffles grouped sequences.
    """
    # Key stretching: 100k rounds to make the alphabet derivation costly
    salt = pack[-1] + seed[-1:] + pack[0] + seed[:1]
    seed = hashlib.pbkdf2_hmac('sha256', seed, salt, 100_000)

    pack_shuffled = b''
    for cut in pack:
        # Shuffle each individual sequence (0-9, a-z, etc)
        pack_shuffled += xcut_shuffle(cut, seed)

    # Final global shuffle for the concatenated result
    return xcut_shuffle(pack_shuffled, seed)

def xh512(data: bytes):
    """
    Generates a 64-character hash (512 bits) using bidirectional diffusion,
    block compression, and dynamic Base64 encoding.
    """
    le = len(data)
    if le == 0: data = b'\x00'

    # 1. Init 512-byte state and RNG based on input data
    rng = random.Random(int.from_bytes(data[:8], 'big') + le)
    b512 = bytearray(((i * 31) ^ data[i % le]) % 256 for i in range(512))

    # 2. Deterministic Shuffle (Fisher-Yates) tied to input values
    for i in range(511, 0, -1):
        j = (data[i % le] + i) % (i + 1)
        b512[i], b512[j] = b512[j], b512[i]

    # 3. Bidirectional Diffusion (forward and backward) for full avalanche effect
    for i in range(1, 512):
        b512[i] = (b512[i] ^ b512[i-1] ^ data[i % le]) % 256
    for i in range(510, -1, -1):
        b512[i] = (b512[i] ^ b512[(i + 1) % 512]) % 256

    # 4. Jump-mix with Bit Rotation (Non-linearity)
    for i in range(512):
        jump_idx = rng.randint(0, 511)
        mixed = b512[i] ^ b512[jump_idx] ^ data[i % le]
        # Circular 3-bit left rotation
        rolled = ((mixed << 3) & 0xFF) | (mixed >> 5)
        b512[i] = (rolled + i) % 256

    # 5. Compression: 512 bytes -> 64 bytes via block mixing
    b64 = bytearray(64)
    rng = random.Random(sum(b512)) # Re-seed with processed state

    for i in range(64):
        block = b512[i*8 : (i+1)*8]
        acc = rng.randint(0, 255)
        for b in block:
            # Chained XOR with RNG jumps
            acc = (acc ^ b ^ rng.randint(0, 255)) % 256

        # Final 4-bit rotation for byte dispersion
        b64[i] = ((acc << 4) & 0xFF | (acc >> 4)) ^ rng.randint(0, 255)

    # 6. Final encode using shuffled alphabet (PBKDF2 internal)
    alphabet = xpack_shuffle(SEQUENCES, bytes(b64)).decode()
    end = []
    for value in b64:
        # Bias-free character selection (Base 64)
        char = alphabet[value % len(alphabet)]
        end.append(char)

    return ''.join(reversed(end))