#!/usr/bin/env python3
from math import isqrt as root
from math import sin, cos
import time, os

MCV = 0xFFFFFFFF # Max constante 32 bits value
PCV = 0x9E3779B9 # Prime constante value

def shake(tokens: bytearray, data: bytes) -> bytearray:
    """ Simple token deterministic shuffle based on data"""
    for a in range(len(tokens)-1, 0, -1):
        ax, ay = jump(len(data), sum(data))
        bx, by = jump(len(tokens), (data[ax] + data[ay]) * (a + 1) ^ (PCV >> 8) ^ tokens[a])
        tokens[bx], tokens[by] = tokens[by], tokens[bx]

    return tokens

def bidirectional_diffusion(tokens: bytearray, data: bytes) -> bytearray:
    """Bidirectional diffusion for avalanche effect"""
    arr_size = len(tokens)
    data_size = len(data)

    # forward ->
    for a in range(1, arr_size):
        tokens[a] = tokens[a] ^ tokens[a-1] ^ data[a % data_size] % 256

    # backward <-
    for a in range(arr_size-2,-1,-1):
        tokens[a] = (tokens[a] ^ tokens[(a + 1) % 512]) % 256
    return tokens


class Seletor:

    @staticmethod
    def mdla(data: bytes, mod: int):
        """Linear edge-based index selection."""
        left, right, size = data[0], data[-1], len(data)
        x = left % size
        y = right % size

        return data[(x*mod)%size], data[(y*mod)%size]

    @staticmethod
    def mdlb(data: bytes, mod: int):
        """Circular bit rotation (ROTL) for non-linear dispersion."""
        size = len(data)
        seed = data[0] ^ data[size // 2] ^ data[-1] ^ size
        h = (seed ^ (mod * 0xcc9e2d51)) & 0xFFFFFFFF
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xe6546b64) & 0xFFFFFFFF
        h = ((h << 17) | (h >> 15)) & 0xFFFFFFFF
        x, y = (h ^ (h >> 7)) % size, (h ^ (h << 11)) % size
        return data[x], data[y]

    @staticmethod
    def mdlc(data: bytes, size: int):
        """Prime-based geometric jump mapping."""
        seed = (data[0] * 31 + data[-1] * 37 + size) & 0xFFFFFFFF
        h = (seed + (size * 0x9e3779b1)) & 0xFFFFFFFF
        x, y = (h * 127) % size, (h * 8191) % size
        return data[x], data[y]

    @staticmethod
    def anchor(data: bytes, mod: int):
        """Anchor-byte dependent state mutation."""
        size = len(data)
        anchor = data[(mod ^ size) % size]
        h = (anchor << 24 | data[0] << 16 | data[-1] << 8 | (mod % 255)) & 0xFFFFFFFF
        h ^= h >> 16
        h = (h * 0x85ebca6b) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 0xc2b2ae35) & 0xFFFFFFFF
        x, y = (h ^ (h >> 16)) % size, (h ^ (h >> 8)) % size
        return data[x], data[y]

# Operações de Bit rápidas
#rolling = lambda v: ((v << 3) & 0xFF | (v >> 5)) & 0xFF
#mixing  = lambda a, b, c: (a ^ b ^ c) & 0xFF
normc   = lambda s, a, b: (root(a**2 + b**2) + (a ^ PCV)) % s

# springs

def mix(a, b, c):
    return (a ^ b ^ c) & 0xFF

def roll(v):
    return ((v << 3) & 0xFF | (v >> 5)) & 0xFF

def gbytes(va):
    if isinstance(va, int):
        le = (va.bit_length() + 7) // 8 or 1
        return bytearray(va.to_bytes(length=le, byteorder='big'))
    elif isinstance(va, str):
        return bytearray(va.encode())
    return bytearray(va)

def jump_vec(normlize: int, value: int):
    # X e Y derivados de COS e SIN
    y = int(abs(sin(value) * MCV))
    x = int(abs(cos(value) * MCV))

    # Aplicamos uma rolagem leve pra eliminar viés normalizando
    y = ((x <<  3) &  0xFF | (x >> 5)) % normlize
    x = ((y <<  3) &  0xFF | (y >> 5)) % normlize
    return x, y

def jump(normalize, value):
    h = (value ^ (value >> 16)) * 0x85ebca6b
    h = (h ^ (h >> 13)) * 0xc2b2ae35
    h = (h ^ (h >> 16)) & 0xFFFFFFFF

    return h % normalize, ((h >> 8) | (h << 24)) % normalize

def spring(va, sb=512):
    avalues = gbytes(va)
    if not avalues: return None

    blen, alen = sb, len(avalues)
    bvalues = bytearray((i * 0x45 + (PCV & 0xFF)) & 0xFF for i in range(blen))
    out = [a for a in bvalues]
    print(out)
    state_v = (sum(avalues) ^ PCV ^ blen) & 0xFF

    for crr in range(blen):

        # State extraction
        a1, a2 = Seletor.anchor(avalues, state_v)
        b1, b2 = Seletor.anchor(bvalues, state_v)

        # Spatial mapping
        ax, ay = jump(alen, (a1 + b1) * (crr + 1) ^ (PCV >> 8) ^ b1 ^ b2)
        bx, by = jump(blen, (a2 + b2) * (crr + 1) ^ (PCV >> 8) ^ a1 ^ a2)

        # Cross-chained mix-roll
        bvalues[bx] = roll(mix(bvalues[by], avalues[ay] ^ a1 ^ b1, state_v))
        bvalues[by] = roll(mix(bvalues[bx], avalues[ax], state_v))

        bvalues[by] = roll(mix(bvalues[bx], avalues[ax] ^ a2 ^ b2, state_v))
        bvalues[bx] = roll(mix(bvalues[by], avalues[ay], state_v))

        # Re-jumping and final swap
        bx, by = jump(blen, bvalues[bx] ^ bvalues[by] ^ b1 ^ b2 ^ 0xFF)
        bvalues[bx], bvalues[by] = bvalues[by], bvalues[bx]

        state_v = (a1 + a2) ^ (b1 + b2) & 0xFF

    return bvalues


if __name__ == '__main__':
    hashs = set()

    maximum = 0xFFFF

    start = time.time()

    hash = bytes(spring(os.urandom(16), 64))
    #for v in range(maximum):
    #    h = bytes(spring(v, 4))
    #    hashs.add(h)

    stop = time.time() - start

    #total = ((len(hashs) / maximum)) * 100
    print(f'[+] Hash: {len(hash)*8}bits em tempo de : {stop:.6f}s')
    #print(f'[>] Total de valores: {maximum}')



