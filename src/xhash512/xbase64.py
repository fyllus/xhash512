#!/usr/bin/env python3

import os
import random

class XBase64():
    """
    Dynamic alphabet and seed generator based on pseudo-random permutations.
    Provides tools for creating deterministic shuffles and high-entropy sequences.
    """

    def __init__(self, seed) -> None:
        """
        Initialize with a base seed and predefined character sequences.
        """
        self.seed = seed
        self.sequences = {
            '0-9': '0123456789',
            'a-f': 'abcdef',
            'g-z': 'ghijklmnopqrstuvwxyz',
            '-+': '-+'
        }

    def x64_base(self, seed='', option: str = 'base64', steps: int = 1) -> bytes:
        """
        Generates a shuffled alphabet based on a specific character set option.

        Args:
            seed: Optional string/bytes to seed the shuffle. Defaults to self.seed.
            option: Character set selection ('base64', 'hex', 'lower', 'upper', 'alpha', 'alnum').
            steps: Number of shuffle iterations to perform.
        """
        _seed = seed or self.seed or os.urandom(16)

        if not isinstance(_seed, (str, bytes)):
            raise ValueError('Seed must be a valid string or bytes')
        if not isinstance(steps, int):
            raise ValueError('Steps must be a valid integer')

        ref = self.sequences
        match option:
            case 'base64':
                alphabet = ref['0-9'] + ref['a-f'] + ref['a-f'].upper() + ref['g-z'] + ref['g-z'].upper() + ref['-+']
            case 'hex':
                alphabet = ref['0-9'] + ref['a-f']
            case 'lower':
                alphabet = ref['a-f'] + ref['g-z']
            case 'upper':
                alphabet = ref['a-f'].upper() + ref['g-z'].upper()
            case 'alpha':
                alphabet = ref['a-f'] + ref['g-z'] + ref['a-f'].upper() + ref['g-z'].upper()
            case 'alnum':
                alphabet = ref['a-f'] + ref['g-z'] + ref['a-f'].upper() + ref['g-z'].upper() + ref['0-9']
            case _:
                alphabet = ref['0-9']

        rng = random.Random(_seed)
        xalphabet = bytearray(alphabet.encode())

        for _ in range(steps):
            rng.shuffle(xalphabet)

        return bytes(xalphabet)

    def x64_rng(self, seed='') -> random.Random:
        """
        Returns a random.Random instance seeded with a high-entropy generated seed.
        """
        _seed = seed or self.seed or os.urandom(16)
        # Derives a deterministic 64-byte seed before initializing the RNG
        derived_seed = self.x64_seed(seed=_seed, steps=min(len(_seed), 10_000))
        return random.Random(derived_seed)

    def x64_seed(self, seed='', steps=1) -> bytes:
        """
        Generates a deterministic 64-byte sequence (512 bits) using a shuffled alphabet.
        """
        _seed = seed or self.seed or os.urandom(16)
        # Number of shuffle steps defaults to seed length for increased complexity
        xalphabet = self.x64_base(seed=_seed, option='base64', steps=(steps or len(_seed)))

        rng = random.Random(_seed)
        sx64 = bytes([rng.choice(xalphabet) for _ in range(64)])

        return sx64