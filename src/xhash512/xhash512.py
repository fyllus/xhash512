#!/usr/bin/env python3
from .xbase64 import XBase64

def deterministic_shuffle(tokens: bytearray, data: bytes) -> bytearray:
    """ Simple token deterministic shuffle based on data"""
    arr_size = len(tokens)
    data_size =  len(data)

    for a in range(arr_size-1, 0, -1):
        b = (data[a % data_size] + a) % (a + 1)
        tokens[a], tokens[b] = tokens[b], tokens[a]

    return tokens


def bidirectional_diffusion(tokens: bytearray, data: bytes) -> bytearray:
    """Bidirectional diffusion for avalanche effect"""
    arr_size = len(tokens)
    data_size = len(data)

    # forward ->
    for a in range(1, arr_size):
        tokens[a] = (tokens[a] ^ tokens[a-1] ^ data[a % data_size]) % 256

    # backward <-
    for a in range(arr_size-2,-1,-1):
        tokens[a] = (tokens[a] ^ tokens[(a + 1) % 512]) % 256

    return tokens

def jump_mix_bit_rotation(tokens: bytearray, data: bytes):
    """Jump-mix with bit rotation"""
    arr_size = len(tokens)
    data_size = len(data)
    rng = XBase64(data).x64_rng()

    for a in range(arr_size):
        jidx = rng.randint(0, arr_size-1)

        mixed = tokens[a] ^ tokens[jidx] ^ data[ a % data_size]
        rolled = ((mixed <<  3) &  0xFF | (mixed >> 5))
        tokens[a] = (rolled + a) % 256

    return tokens


def byte_derivator(data: bytes, tokens: int) -> bytearray:
    """Simple data byte derivator"""

    size = len(data)
    if size == 0:
        data = b'\x00'

    rng = XBase64(data).x64_rng()
    xbytes = bytearray(tokens)

    for i in range(tokens):
        # Get 3 modifiers deterministic rng selected
        amod, bmod, cmod = data[rng.randint(0, size-1)], data[rng.randint(0, size-1)], data[rng.randint(0, size-1)]
        # Aply XOR operation for each byte with
        xbytes[i] = ((i * 31) ^ amod ^ bmod ^ cmod) % 256
    return xbytes


def xh512(data: bytes) -> bytes:
    """
    Generates a 512-bit (64-character) hash using bidirectional diffusion,
    non-linear bit rotation, and dynamic Base64 encoding.
    Args:
        data: Input bytes to be hashed.

    Returns:
        A 64-byte deterministic hash string.
    """
    if len(data) == 0:
        data = b'\x00'

    # Derivate and Deterministic Shuffle (Fisher-Yates) tied to input values
    b512 = deterministic_shuffle(byte_derivator(data, 512), data)

    # Bidirectional Diffusion and Jmp-mix with BIT ROTATION (Non-linearity)
    b512 = jump_mix_bit_rotation( bidirectional_diffusion(b512, data) , data)

    # Derivation Compression: 512 bytes -> 64 bytes via block mixing
    b64 = byte_derivator(bytes(b512), 64)

    rng = XBase64(bytes(b512)).x64_rng() # Re-seed RNG 512-byte state

    for i in range(64):
        block = b512[i*8 : (i+1)*8]
        acc = rng.randint(0, 255)
        for b in block:

            # Chained XOR with RNG-driven jumps
            acc = (acc ^ b ^ rng.randint(0, 255)) % 256

        # Final 4-bit rotation for byte dispersion
        b64[i] = ((acc << 4) & 0xFF | (acc >> 4)) ^ rng.randint(0, 255)

    # Final encode using shuffled dynamic alphabet
    base = XBase64(bytes(b64))
    alphabet = base.x64_base(steps=min(len(data), 256)).decode()
    end = []
    for value in b64:
        # Map compressed bytes to the dynamic alphabet
        char = alphabet[value % len(alphabet)]
        end.append(char)

    # Reverse and return as bytes for consistency
    return ''.join(reversed(end)).encode()

