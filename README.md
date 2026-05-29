# xhash

**Version:** 0.4.2

**Author:** Fyllus (Geliardi D. Oliveira)

**License:** MIT

> **Notice:** `xhash` is an independent, lightweight hashing library designed for high-entropy identification and data obfuscation. It has not undergone formal cryptographic auditing and is intended for research, quick lookup indexes, and personal development environments.

---

# 🛠 Features

* **Procedural Architecture:** Completely decoupled from complex object states. Pure functions and streamlined structures maximize execution speed.
* **Non-Linear Bit Fabric:** Implements `bit_rotate` with cross-XOR mechanics and dynamic bit shifts, shattering predictable data patterns.
* **Dynamic Tokenization:** Uses zero-copy `memoryview` slicing to break inputs into variable-length blocks dynamically based on the input byte stream.
* **Cascade Absorption:** Employs a bidirectional permutation-substitution matrix where tokens alter future state anchors concurrently.
* **Deterministic Native PRNG:** Includes `XBase64` driven by `pseudo_random_states`, an isolated finite state machine that shuffles alphabets and selects high-entropy sequences without relying on Python's built-in `random` module.

---

# 🏗 Pipeline Architecture

```
[ Input Data ] ──> [ dynamic_tokenize ] ──> [ absorb_tokens ] ──> [ compress_blocks ] ──> [ Hex Output ]

```

### 1. Dynamic Tokenization

* **Zero-Copy Slicing:** Wraps inputs in a `memoryview` to prevent memory reallocation.
* **Variable Stride:** The current byte determines the sizing stride modulo (`view[idx] % chunk_limit`), outputting variable-length binary tokens.

### 2. Chain Absorption

* **Positional Modifiers:** Generates scaling factors (`l_shift`, `r_shift`, `xor_mask`) based on the token index.
* **Accumulator Avalanche:** Compresses values into 64-bit bounded chaotic feedback blocks. A single bit variation in the input completely alters the subsequent tracking state.

### 3. Substitution-Permutation Matrix

* **State Buffer Seeding:** Initializes a `bytearray` buffer scaled exactly to the requested output size.
* **Dual-Index Cross-Linked Feedback:** Traverses data blocks and applies bidirectional bitwise rotation, mutating `buffer[idx_x]` and `buffer[idx_y]` simultaneously based on calculated indices.


> 📘 For comprehensive mathematical formulas and low-level execution logs, see the detailed [Pipeline Architecture Documentation](docs/PIPELINE.md).

---
---

# 🚀 Installation

```bash
git clone https://github.com/fyllus/xhash.git && ( cd xhash && pip install . )

```

---

# 💻 Usage

```python
import xhash

data = "apenas um teste qualquer"

# Generate hashes of standard bit widths
hash_512 = xhash.xhash512(data)
hash_256 = xhash.xhash256(data)
hash_128 = xhash.xhash128(data)
hash_64  = xhash.xhash64(data)

print(f"Hex 512: {hash_512}")
print(f"Hex 64:  {hash_64}")

# Generate custom byte sizes directly
custom_hash = xhash.xhash_dyna(data, size=7)
print(f"Hex 56-bit (7 bytes): {custom_hash}")

```

### Dynamic Alphabet Generation (`XBase64`)

```python
from xhash import XBase64

engine = XBase64(seed="my_secure_seed")

# Generate a deterministically shuffled Base64 alphabet
shuffled_alpha = engine.x64_base(option="base64", steps=5)
print(f"Custom Alphabet: {shuffled_alpha.decode()}")

```

---

# 🧪 Development Roadmap

* [x] Refactor core architecture from Object-Oriented to explicit pipeline functions.
* [x] Achieve 0.00% collision rate across 1,000,000 sequential entries at 64-bit (8 bytes).
* [x] Achieve 0.00% collision rate across 1,000,000 high-entropy PRNG entries at 56-bit (7 bytes).
* [ ] Implement a CLI tool for direct file hashing and throughput benchmarking.
* [ ] Port the underlying `bit_rotate` and permutation loops to a native C Python Extension.

### Validation

* **56-bit Boundary Exhaustion:** Successfully passed exhaustive pseudo-random sequential stress tests up to 1,000,000 entries with zero duplicate mappings on a strict 7-byte layout.
* **10M Saturation Breakthrough:** Verified 0.00000% collision rate across 10,000,000 continuous long-block inputs in cloud environments. Read the full [Technical Validation Report](docs/VALIDATION.md).
---

# 📝 Release Notes (v0.4.0-stable)

### Architectural Shift

* **Clean & Functional:** Eliminated class instantiation requirements for hashing operations. Package exposes fast, direct procedural functions (`xhash512`, `xhash256`, etc.).
* **Zero-External-RNG:** Replaced all leftover `random.Random` calls inside alphabet generation with native `pseudo_random_states` loops, establishing 100% internal mathematical consistency.

### Performance & Optimization

* **Memory Protection:** Slicing loops completely rely on memory arrays, drastically improving execution performance for larger blocks.
* **Sub-45s 1kk Stress Scaling:** Able to process 1,000,000 chaotic FSM mutations and verify zero collisions under 43 seconds in standard Python interpreter setups.

### Validation

* **56-bit Boundary Exhaustion:** Successfully passed exhaustive pseudo-random sequential stress tests up to 1,000,000 entries with zero duplicate mappings on a strict 7-byte layout.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.