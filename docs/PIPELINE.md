
# Data Processing Pipeline

The `xhash` execution pipeline transforms arbitrary inputs into highly diffused, fixed-length hexadecimal strings through a deterministic, three-stage execution matrix.

```
[ Input Data ] ──> Step 1: Tokenize ──> Step 2: Absorb ──> Step 3: Compress ──> [ Hex Digest ]

```

---

## Step 1: Dynamic Tokenization

The input data is mapped into a non-copying memory layer and sliced into variable-length binary tokens. Slicing boundaries are dictated dynamically by the input byte stream values, preventing structural preprocessing patterns.

```python
from xhash import xhashlib as xl

data = "Lorem Ipsum is simply dummy text of the printing and typesetting industry.\n\n"
tokens = xl.dynamic_tokenize(data)

```

### Binary Representation Output

```python
[
    b'\nL', b'ore', b'm', b' ', b'I', b'p', b'sum', b' ', b'i', b's s', b'i', b'm', b'p', b'l', 
    b'y', b' ', b'd', b'u', b'm', b'm', b'y', b' ', b't', b'e', b'x', b't', b' ', b'of ', b't', 
    b'h', b'e', b' ', b'p', b'ri', b'nt', b'i', b'ng', b' ', b'a', b'nd', b' ', b't', b'y', b'p', b'e', 
    b'set', b't', b'i', b'ng', b' ', b'i', b'nd', b'u', b'str', b'y', b'.\n', b'\n'
]

```

---

## Step 2: Cascade Token Absorption

The extracted variable-length tokens are compressed sequentially into strict 64-bit (8-byte) feedback state blocks. A sliding index injects positional modifiers (`l_shift`, `r_shift`, `xor_mask`), forcing an immediate avalanche effect across subsequent iterations.

```python
absorbed_blocks = xl.absorb_tokens(tokens)

```

### 64-bit Bounded State Output

```python
[
    b'\xd2\xf6\xedXQ\xa5\x00\x82', b'\xf5\xd1B:\xa50\x8d\x0e', 
    b'\xe1\xaf\xb6\xd9\xf5v\x91\xa4', b'\xdf\xe7\xb3\x10w\x04\x1c\xe7', 
    b'\x85(\x8a0\xa3\xcd2%', b'\xa6\x1e$t\xef\xa9?&', 
    b'\xde_\xc1\xc1\xca\xd6\xa6\xac', b'\x9c\x13!+p?\x8a\xab', 
    b'\xb6\xc2\xbd\x9bPn\xba\xd4', b'\xc6\xf8\xde\xeeH\x0c^\x97', 
    b'\x8d\r\xefcK\x1b\xf8\x0f', b'\x96M\x9d\xe97i\xb8p', 
    b'\xff\x99\x84U\xad5\x1cr', b'\x97>T\xba\xf9:\xbcG', 
    b'\xa2\x88\xc2\xccJzn\x82', b'\xc9\t\xf8\xf2"t\xf7\xa2', 
    b'\xed\xd6\n\xd6\xe6p\xcb\xfc', b'\x8e+ \x1fq<\x88\xad', 
    b'\xbb\xc3\x92\xb4n\xb5C\xd4', b'\xe0\xb6y\x8e\xc8\x8f\x87l', 
    b"P'P\x1c\na"
]

```

---

## Step 3: Permutation-Substitution Matrix Compression

The 8-byte state blocks pass through a bi-directional permutation matrix. Instead of using predefined word/dword lookups, the engine derives a highly chaotic state buffer using an isolated FSM initialized by a dynamic pivot seed.

```python
compressed_hex = xl.compress_blocks(absorbed_blocks, output_size=16)

```

### Underlying Core Mechanics

1. **State Buffer Seeding:** A pivot block is extracted via `31 % len(chain_blocks)` to isolate a deterministic seed.
2. **FSM Buffer Initialization:** The target state array is pre-allocated with values generated via `pseudo_random_states` under an `0xFF` mask.
3. **Cross-Linked Index Mixing:** The matrix traverses every byte of every block, continuously computing shifting cross-references (`idx_x`, `idx_y`) that tie the entire history of the chain together.

```python
# Processing Loop Execution Model
for block in chain_blocks:
    int_block = int.from_bytes(block, byteorder='big')
    for byte in block:
        idx_x = (seed ^ int_block ^ byte) % buf_len
        idx_y = int_block % buf_len

        # Interlinked cascade feedback
        buffer[idx_x] = bit_rotate((buffer[idx_y] ^ byte ^ idx_x ^ buffer[idx_x]), idx_y + byte_counter, 0xFF)
        buffer[idx_y] = bit_rotate((buffer[idx_x] ^ byte ^ idx_y ^ buffer[idx_y]), idx_x + byte_counter, 0xFF)
        byte_counter += 1

```

### Finalized Hexadecimal Hash Output

```text
85bf8b06b2167f1f8e67f640ae36f7ac

```

---

## Core Primitive: Mathematical Bit Rotation (`bit_rotate`)

The structural integrity and non-linearity of the execution layer rely on the internal `bit_rotate` primitive. This core driver destroys algebraic patterns using a 64-bit wide bitwise fabric before applying the required output truncation.

```python
# 1. 64-bit Wide Chaotic Scaling Engine
a = ((value << 16) ^ position ^ (value >> 5)) & 0xFFFFFFFFFFFFFFFF
b = ((value << 11) ^ position ^ (value >> 3)) & 0xFFFFFFFFFFFFFFFF

# 2. Intertwined Variable Bitwise Cross-Rotation
rotated_state = ((a << (b & 0xF)) ^ position ^ (b >> (a & 0xF))) & output_mask

```