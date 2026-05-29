#!/usr/bin/env python3
"""
xhash main execution module.

Provides explicit cryptographic wrappers for the xhash pipeline,
supporting output configurations from 64-bit up to 512-bit sizes.
"""

from .xhashlib import dynamic_tokenize, absorb_tokens, compress_blocks


def xhash_dyna(data, size: int = 64) -> str:
    """Executes the complete xhash pipeline with a dynamic output size.

    Args:
        data (str | bytes | int): Raw input data to be digested.
        size (int): Final output size in bytes. Defaults to 64.

    Returns:
        str: Hexadecimal string representation of the digested data.
    """
    tokens = dynamic_tokenize(data=data)
    mutate = absorb_tokens(tokens=tokens)
    return compress_blocks(chain_blocks=mutate, output_size=size)


def xhash512(data) -> str:
    """Generates a 512-bit (64-byte) hash digest.

    Args:
        data (str | bytes | int): Raw input data to be digested.

    Returns:
        str: A 128-character hexadecimal string.
    """
    return xhash_dyna(data)


def xhash256(data) -> str:
    """Generates a 256-bit (32-byte) hash digest.

    Args:
        data (str | bytes | int): Raw input data to be digested.

    Returns:
        str: A 64-character hexadecimal string.
    """
    return xhash_dyna(data, size=32)


def xhash128(data) -> str:
    """Generates a 128-bit (16-byte) hash digest.

    Args:
        data (str | bytes | int): Raw input data to be digested.

    Returns:
        str: A 32-character hexadecimal string.
    """
    return xhash_dyna(data, size=16)


def xhash64(data) -> str:
    """Generates a 64-bit (8-byte) hash digest.

    Args:
        data (str | bytes | int): Raw input data to be digested.

    Returns:
        str: A 16-character hexadecimal string.
    """
    return xhash_dyna(data, size=8)


if __name__ == '__main__':
    teste = 'apenas um teste qualquer'
    print(xhash512(teste))

