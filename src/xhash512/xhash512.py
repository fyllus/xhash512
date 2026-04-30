#!/usr/bin/env python3
from functools import total_ordering
from .xbase64 import XBase64
from . import tools

MODS = [ tools.mdl1, tools.mdl2, tools.mdl3, tools.mdl5, tools.mdl5]

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

    for a in range(arr_size):
        jidx = ((a + 1) * tokens[a] ^ 0x9E3779B9 ^ data_size) % arr_size

        mixed = tokens[a] ^ tokens[jidx] ^ data[ a % data_size]
        rolled = ((mixed <<  3) &  0xFF | (mixed >> 5))
        tokens[a] = (rolled + a) % 256

    return tokens

class XHash():
    def __init__(self, mods: int = 2) -> None:
        self.mods = MODS[:max(1, min(mods, len(MODS)))]

    def xh512(self, data):
        """
        Generates a 512-bit (64-character) hash using bidirectional diffusion,
        non-linear bit rotation, and dynamic Base64 encoding.
        Args:
            data: Input bytes to be hashed.

        Returns:
            A 64-byte deterministic hash string.
        """
        data = self.validate_input(data)
        if len(data) == 0:
            data = b'\x00'

        # Derivate and Deterministic Shuffle (Fisher-Yates) tied to input values
        b512 = deterministic_shuffle(self.derivator(data, 512), data)

        # Bidirectional Diffusion and Jmp-mix with BIT ROTATION (Non-linearity)
        b512 = jump_mix_bit_rotation( bidirectional_diffusion(b512, data) , data)

        # Derivation Compression: 512 bytes -> 64 bytes via block mixing
        b64 = self.derivator(bytes(b512), 64)

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

    def validate_input(self, data) -> bytes:
        if isinstance(data, str):
            return data.encode()
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)
        if isinstance(data, int):

            length = (data.bit_length() + 7) // 8 or 1
            return data.to_bytes(length, byteorder='big')

        return str(data).encode()

    def derivator(self, data: bytes, tokens: int):
        """Simple data byte derivator"""
        size = len(data)
        if size == 0:
            data = b'\x00'
        xbytes = bytearray(tokens)
        for i in range(tokens):

            # Vector modifier
            apply = self.mods[(i*size^8)%(len(self.mods))]
            amod, bmod, cmod = apply(data, i)

            # Aply XOR operation for each byte with
            xbytes[i] = ((i * 31) ^ amod ^ bmod ^ cmod) % 256

        return xbytes

