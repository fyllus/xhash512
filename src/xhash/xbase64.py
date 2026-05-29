#!/usr/bin/env python3
"""
XBase64 alphabet and seed generator.

Utilizes the xhashlib core engine to perform deterministic, high-entropy
permutations and sequence generation without external random dependencies.
"""

import os
from collections.abc import Iterator
from .xhashlib import dynamic_tokenize, absorb_tokens, compress_blocks, pseudo_random_states


class XBase64:
    """Dynamic alphabet and seed generator based on xhashlib permutations.

    Provides tools for creating deterministic shuffles and high-entropy sequences.
    """

    def __init__(self, seed) -> None:
        """Initialize with a base seed and predefined character sequences."""
        self.seed = seed
        self.sequences = {
            '0-9': '0123456789',
            'a-f': 'abcdef',
            'g-z': 'ghijklmnopqrstuvwxyz',
            '-+': '-+'
        }

    def _derive_numeric_seed(self, seed_data: str | bytes) -> int:
        """Internal helper to compress any seed into a valid 64-bit integer anchor."""
        tokens = dynamic_tokenize(seed_data)
        blocks = absorb_tokens(tokens)
        # Uses the standard 8-byte digest approach to extract a 64-bit integer
        hex_digest = compress_blocks(blocks, output_size=8)
        return int(hex_digest, 16)

    def _deterministic_shuffle(self, data: bytearray, seed_int: int) -> None:
        """Applies an in-place Fisher-Yates shuffle driven by pseudo_random_states."""
        size = len(data)
        if size <= 1:
            return

        # Generates a chaotic stream of indexes bounded by the remaining array size
        state_generator = pseudo_random_states(seed_int, size - 1, output_mask=0xFFFFFFFFFFFFFFFF)

        for i, (_, rand_val) in enumerate(state_generator):
            # Clamps the random state to the available slicing window
            j = i + (rand_val % (size - i))
            data[i], data[j] = data[j], data[i]

    def x64_base(self, seed='', option: str = 'base64', steps: int = 1) -> bytes:
        """Generates a shuffled alphabet based on a specific character set option.

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
                alphabet = ref['0-9'] + ref['a-f'] + ref['a-f'].upper() + ref['g-z'] + ref['g-z'].upper() + ref['-+' ]
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

        xalphabet = bytearray(alphabet.encode())
        seed_anchor = self._derive_numeric_seed(_seed)

        # Cascades the shuffle steps by feeding back the modified anchor
        for step in range(steps):
            self._deterministic_shuffle(xalphabet, seed_anchor + step)

        return bytes(xalphabet)

    def x64_rng(self, seed='') -> Iterator[int]:
        """Returns a state-isolated pseudo-random generator stream from the current engine."""
        _seed = seed or self.seed or os.urandom(16)
        derived_seed = self._derive_numeric_seed(_seed)
        # Replaces random.Random instance with an infinite generator loop
        return pseudo_random_states(derived_seed, size=0xFFFFFFFFFFFFFFFF, output_mask=0xFFFFFFFFFFFFFFFF)

    def x64_seed(self, seed='', steps=1) -> bytes:
        """Generates a deterministic 64-byte sequence (512 bits) using a shuffled alphabet."""
        _seed = seed or self.seed or os.urandom(16)

        # Generates the target shuffled space
        shuffle_steps = steps or (len(_seed) if isinstance(_seed, (str, bytes)) else 1)
        xalphabet = self.x64_base(seed=_seed, option='base64', steps=shuffle_steps)
        alpha_len = len(xalphabet)

        seed_anchor = self._derive_numeric_seed(_seed)
        state_generator = pseudo_random_states(seed_anchor ^ 0x5555555555555555, size=64, output_mask=0xFFFFFFFFFFFFFFFF)

        # Replaces rng.choice with state-driven modular index selection
        output_buffer = bytearray(64)
        for idx, (_, rand_val) in enumerate(state_generator):
            output_buffer[idx] = xalphabet[rand_val % alpha_len]

        return bytes(output_buffer)