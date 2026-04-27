#!/usr/bin/env python3

from xbase64 import XBase64

def xh512(data: bytes) -> bytes:
    """
    Generates a 512-bit (64-character) hash using bidirectional diffusion,
    non-linear bit rotation, and dynamic Base64 encoding.
    Args:
        data: Input bytes to be hashed.

    Returns:
        A 64-byte deterministic hash string.
    """
    le = len(data)
    if le == 0:
        data = b'\x00'

    # 1. Init 512-byte state and custom RNG based on input data
    x64 = XBase64(data)
    rng = x64.x64_rng()
    b512 = bytearray(((i * 31) ^ data[i % le]) % 256 for i in range(512))

    # 2. Deterministic Shuffle (Fisher-Yates) tied to input values
    for i in range(511, 0, -1):
        j = (data[i % le] + i) % (i + 1)
        b512[i], b512[j] = b512[j], b512[i]

    # 3. Bidirectional Diffusion for full avalanche effect
    # Forward pass
    for i in range(1, 512):
        b512[i] = (b512[i] ^ b512[i-1] ^ data[i % le]) % 256
    # Backward pass
    for i in range(510, -1, -1):
        b512[i] = (b512[i] ^ b512[(i + 1) % 512]) % 256

    # 4. Jump-mix with Bit Rotation (Non-linearity)
    for i in range(512):
        jump_idx = rng.randint(0, 511)
        mixed = b512[i] ^ b512[jump_idx] ^ data[i % le]
        # Circular 3-bit left rotation (ROL)
        rolled = ((mixed << 3) & 0xFF) | (mixed >> 5)
        b512[i] = (rolled + i) % 256

    # 5. Compression: 512 bytes -> 64 bytes via block mixing
    b64 = bytearray(64)
    # Re-seed RNG using the fully diffused 512-byte state
    rng = XBase64(bytes(b512)).x64_rng()

    for i in range(64):
        block = b512[i*8 : (i+1)*8]
        acc = rng.randint(0, 255)
        for b in block:
            # Chained XOR with RNG-driven jumps
            acc = (acc ^ b ^ rng.randint(0, 255)) % 256

        # Final 4-bit rotation for byte dispersion
        b64[i] = ((acc << 4) & 0xFF | (acc >> 4)) ^ rng.randint(0, 255)

    # 6. Final encode using shuffled dynamic alphabet
    alphabet = x64.x64_base(steps=min(len(data), 256)).decode()
    end = []
    for value in b64:
        # Map compressed bytes to the dynamic alphabet
        char = alphabet[value % len(alphabet)]
        end.append(char)

    # Reverse and return as bytes for consistency
    return ''.join(reversed(end)).encode()