#!/usr/bin/env python3
"""
xhashlib core engine module.

Implements the underlying bitwise operations, tokenization, absorption,
and substitution-permutation network for the xhash pipeline.
"""

from collections.abc import Iterator

def bit_mask(value, bits_len=64):
    """
    Apply a bit-level mask (1, 3, 7, 15...) in O(1) time complexity.

    Args:
        value (int): The target integer to be masked.
        bits_len (int): Number of bits to stack from right to left. Max bound: 64.
    """
    bits_len = (bits_len % 65) or 1
    mask = (1 << bits_len) - 1
    return value & mask

def nibble_mask(value, amount=16):
    """
    Apply a hexadecimal nibble-level mask (0xF, 0xFF, 0xFFF...) in O(1) time complexity.

    Args:
        value (int): The target integer to be masked.
        amount (int): Number of 4-bit nibbles to stack. Max bound: 16 (64-bit block).
    """
    amount = (amount % 17) or 1
    mask = (1 << (amount * 4)) - 1
    return value & mask

def bit_rotate(value: int, position: int = 1, bits: int = 64) -> int:
    """
    Apply non-linear bitwise shifts and cross-XOR rotations under a strict 64-bit fabric.

    Args:
        value (int): Input bits to rotate.
        position (int): Positional offset applied as a salt during shifts. Defaults to 1.
        bits (int): Final bit size to clamp the returned value. Defaults to 64.

    Returns:
        int: Fully diffused and masked integer.
    """
    a = nibble_mask(((value << 16) ^ position ^ (value >> 5)), 16)
    b = nibble_mask(((value << 11) ^ position ^ (value >> 3)), 16)
    return bit_mask(((a << (b & 0xF)) ^ position ^ (b >> (a & 0xF))), bits)


def get_byte_length(value: int) -> int:
    """Calculates the minimal byte length required to represent an integer.

    Args:
        value (int): The target integer.

    Returns:
        int: Minimum number of bytes required (at least 1).
    """
    return (value.bit_length() + 7) // 8 or 1


def int_to_bytes(value: int, length: int = None, byteorder: str = 'big') -> bytes:
    """Converts an integer into its dense byte representation.

    Args:
        value (int): Integer to convert.
        length (int): Optional explicit byte length.
        byteorder (str): Byte ordering ('big' or 'little'). Defaults to 'big'.

    Returns:
        bytes: Raw byte representation.
    """
    len_to_use = length if length is not None else get_byte_length(value)
    return int.to_bytes(value, length=len_to_use, byteorder=byteorder)


def get_mix_modifiers(position: int, value: int) -> tuple[int, int, int]:
    """Generates position-dependent state scaling factors and XOR offsets.

    Args:
        position (int): Token position index within the chain.
        value (int): Numeric value of the current token block.

    Returns:
        tuple[int, int, int]: Contains (l_shift, xor_mask, r_shift).
    """
    l_shift = (((position << 8) ^ value ^ (position >> 3)) % 11) or 1
    r_shift = (((position >> 3) ^ value ^ (position << 16)) % 5) or 1
    xor_mask = (value << 13) ^ position ^ (value >> 4)
    return l_shift, xor_mask, r_shift


def pseudo_random_states(seed: int, size: int = 64, bits: int = 8) -> Iterator[tuple[int, int]]:
    """State-isolated finite state machine PRNG.

    Yields high-entropy sequences while protecting the master state from direct exposure.

    Args:
        seed (int): Initial anchor for the generator state.
        size (int): Number of iterations to perform. Defaults to 64.
        bits (int): Bitmask limit for the emitted node. Defaults to 8 (1 byte).

    Yields:
        Iterator[tuple[int, int]]: Index step and the derived pseudo-random integer.
    """
    counter = 1
    state = bit_rotate(seed)
    while counter < size + 1:
        derived_node = bit_rotate(value=state ^ seed, position=counter, bits=bits)
        yield counter - 1, derived_node
        state = bit_rotate(state ^ seed, counter)
        counter += 1


def dynamic_tokenize(data, chunk_limit: int = 4) -> list[bytes]:
    """Slices inputs into variable-length binary tokens using non-copying memoryviews.

    Args:
        data (str | bytes | int): Raw input data.
        chunk_limit (int): Upper bound modulo for dynamic boundary splitting. Defaults to 4.

    Returns:
        list[bytes]: Extracted variable-sized binary chunks.
    """
    if isinstance(data, str):
        raw_bytes = data.encode()
    elif isinstance(data, (bytes, bytearray)):
        raw_bytes = data
    elif isinstance(data, int):
        raw_bytes = int_to_bytes(data)
    else:
        raise TypeError('Unsupported input type: str, bytes, or int required')

    tokens = []
    view = memoryview(raw_bytes)
    total_len = len(view)
    idx = 0
    while idx < total_len:
        stride = min(total_len - idx, (view[idx] % chunk_limit) or 1)
        tokens.append(view[idx : idx + stride].tobytes())
        idx += stride
    return tokens


def absorb_tokens(tokens: list[bytes]) -> list[bytes]:
    """Processes sequential tokens into 64-bit bounded chaotic feedback blocks.

    Destroys linear input structures through position-bound cascade mutation.

    Args:
        tokens (list[bytes]): Chunks generated by the tokenizer stage.

    Returns:
        list[bytes]: 64-bit wide processed state blocks.
    """
    blocks = []
    accumulator = 0
    for pos, token in enumerate(tokens):
        val = int.from_bytes(token, byteorder='big')
        l_shift, xor_mask, r_shift = get_mix_modifiers(pos, val)

        mixed_state = ((accumulator ^ xor_mask) << l_shift) ^ val ^ ((accumulator ^ xor_mask) >> r_shift)
        accumulator = bit_rotate(mixed_state, pos)

        if accumulator.bit_length() >= 64:
            clamped = bit_mask(accumulator, 64)
            blocks.append(int_to_bytes(clamped, length=8))
            accumulator = 0

    if accumulator > 0:
        blocks.append(int_to_bytes(bit_mask(accumulator, 64)))
    return blocks


def compress_blocks(chain_blocks: list[bytes], output_size: int = 7) -> str:
    """Executes a dual-index bi-directional permutation-substitution matrix over the buffer.

    Injects data blocks concurrently using cross-linked array feedback indices.

    Args:
        chain_blocks (list[bytes]): State blocks coming from the absorption phase.
        output_size (int): Expected final hash width in bytes. Defaults to 7.

    Returns:
        str: Hexadecimal string of the finalized compressed buffer.
    """
    pivot_block = chain_blocks[31 % len(chain_blocks)]
    seed = int.from_bytes(pivot_block, byteorder='big')

    buffer = bytearray(val for _, val in pseudo_random_states(seed=seed, size=output_size, bits=8))
    buf_len = len(buffer)

    byte_counter = 0
    for block in chain_blocks:
        int_block = int.from_bytes(block, byteorder='big')
        for byte in block:
            idx_x = (seed ^ int_block ^ byte) % buf_len
            idx_y = int_block % buf_len

            prev_x = buffer[idx_x]
            prev_y = buffer[idx_y]

            buffer[idx_x] = bit_rotate(
                value=(prev_y ^ byte ^ idx_x ^ prev_x),
                position=idx_y + byte_counter,
                bits=8
            )
            buffer[idx_y] = bit_rotate(
                value=(buffer[idx_x] ^ byte ^ idx_y ^ prev_y),
                position=idx_x + byte_counter,
                bits=8
            )
            byte_counter += 1

    return buffer.hex()


def lightweight_hash(data, size: int = 7) -> str:
    """Main pipeline execution hook. Wraps tokenization, absorption, and compression.

    Args:
        data (str | bytes | int): Target input.
        size (int): Desired output digest size in bytes. Defaults to 7.

    Returns:
        str: Finalized lowercase hexadecimal string representation.
    """
    return compress_blocks(absorb_tokens(dynamic_tokenize(data)), size)