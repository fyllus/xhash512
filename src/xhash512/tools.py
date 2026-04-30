#!/usr/bin/env python3

class MODFIERS:

    @staticmethod
    def mdl1(data: bytes, mod: int):
        """Linear edge-based index selection."""
        left, right, size = data[0], data[-1], len(data)
        x = left % size
        y = right % size
        z = ((x + y) ^ size * 256) % size
        return data[(x*mod)%size], data[(y*mod)%size], data[(z*mod)%size]

    @staticmethod
    def mdl2(data: bytes, mod: int):
        """Golden ratio and Murmur-style bit mixing."""
        size = len(data)
        seed = data[0] ^ data[size // 2] ^ data[-1] ^ size
        h = (seed + mod + 0x9E3779B9) & 0xFFFFFFFF
        h ^= (h >> 16)
        h = (h * 0x85ebca6b) & 0xFFFFFFFF
        h ^= (h >> 13)
        h = (h * 0xc2b2ae35) & 0xFFFFFFFF
        h ^= (h >> 16)
        x, y, z = h % size, (h ^ 0x517cc1b7) % size, (h + (h >> 8)) % size
        return data[x], data[y], data[z]

    @staticmethod
    def mdl3(data: bytes, mod: int):
        """Circular bit rotation (ROTL) for non-linear dispersion."""
        size = len(data)
        seed = data[0] ^ data[size // 2] ^ data[-1] ^ size
        h = (seed ^ (mod * 0xcc9e2d51)) & 0xFFFFFFFF
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xe6546b64) & 0xFFFFFFFF
        h = ((h << 17) | (h >> 15)) & 0xFFFFFFFF
        x, y, z = h % size, (h ^ (h >> 7)) % size, (h ^ (h << 11)) % size
        return data[x], data[y], data[z]

    @staticmethod
    def mdl4(data: bytes, mod: int):
        """Prime-based geometric jump mapping."""
        size = len(data)
        seed = (data[0] * 31 + data[-1] * 37 + size) & 0xFFFFFFFF
        h = (seed + (mod * 0x9e3779b1)) & 0xFFFFFFFF
        x, y, z = (h * 13) % size, (h * 127) % size, (h * 8191) % size
        return data[x], data[y], data[z]

    @staticmethod
    def mdl5(data: bytes, mod: int):
        """Anchor-byte dependent state mutation."""
        size = len(data)
        anchor = data[(mod ^ size) % size]
        h = (anchor << 24 | data[0] << 16 | data[-1] << 8 | (mod % 255)) & 0xFFFFFFFF
        h ^= h >> 16
        h = (h * 0x85ebca6b) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 0xc2b2ae35) & 0xFFFFFFFF
        x, y, z = (h ^ (h >> 16)) % size, (h ^ (h >> 8)) % size, (h ^ anchor) % size
        return data[x], data[y], data[z]



__MODS__ = [MODFIERS.mdl1, MODFIERS.mdl2, MODFIERS.mdl3, MODFIERS.mdl4, MODFIERS.mdl5]