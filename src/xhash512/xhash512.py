#!/usr/bin/env python3
from functools import total_ordering
from .xbase64 import XBase64
from .tools import jump_fast, spring, shake, PCV


class XHash():
    def __init__(self, mods: int = 2) -> None:
        pass

    def xh512(self, data):
        """
        Generates a 512-bit (64-character) hash using bidirectional diffusion,
        non-linear bit rotation, and dynamic Base64 encoding.
        """
        data = self.validate(data)
        if len(data) == 0:
            data = b'\x00'

        # Derivate and Deterministic Shuffle (Fisher-Yates) tied to input values
        b512 = shake(self.spring(data, 512), data)

        # Derivation Compression: 512 bytes -> 64 bytes via block mixing
        b64 = self.spring(bytes(b512), 64)

        rng = XBase64(bytes(b512)).x64_rng() # Re-seed RNG 512-byte state

        for i in range(64):
            block = b512[i*8 : (i+1)*8]
            acc = rng.randint(0, 255)
            for b in block:

                # Chained XOR with RNG-driven jumps
                acc = (acc ^ b ^ rng.randint(0, 255)) % 256

            # Final 4-bit rotation for byte dispersion
            b64[i] = ((acc << 4) & 0xFF | (acc >> 4)) ^ rng.randint(0, 255)

        return b64.hex()
        # Final encode using shuffled dynamic alphabet
        #base = XBase64(bytes(b64))
        #alphabet = base.x64_base(steps=min(len(data), 256)).decode()
        #end = []
        #for value in b64:
            # Map compressed bytes to the dynamic alphabet
          #  char = alphabet[value % len(alphabet)]
         #   end.append(char)

        # Reverse and return as bytes for consistency
        #return ''.join(reversed(end)).encode()

    def validate(self, data) -> bytes:
        if isinstance(data, str):
            return data.encode()
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)
        if isinstance(data, int):

            length = (data.bit_length() + 7) // 8 or 1
            return data.to_bytes(length, byteorder='big')

        return str(data).encode()

    def spring(self, data: bytes, tokens: int):
        """Simple data byte spring"""
        return spring(data, tokens)

