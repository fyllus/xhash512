# xHash512
**EXPERIMENTAL:**

---

**Version:** 0.3.0-stable
**Author:** fyllus
**License:** MIT

`xHash512` is an experimental, non-standard hashing library designed for high-entropy unique identification and data obfuscation. It generates a 512-bit (64-character) fixed-length digest through a multi-stage pipeline of bidirectional diffusion, non-linear bit rotation, and dynamic alphabet encoding.

---

# 🛠 Features

*   **Modular Architecture:** Decoupled logic using `XBase64` (entropy engine) and `XHash` (core hashing).
*   **Bidirectional Diffusion:** Dual-pass XOR chains ensure that a single-bit change ripples across the entire 512-byte internal state.
*   **Non-Linearity:** Implements circular bit shifts (ROL) and deterministic jump-mixing to mitigate linear algebraic analysis.
*   **Dynamic MDL System:** Orchestrates up to 5 vector modifier functions $(x, y, z)$ to alternate derivation logic.
*   **Alphabet Shuffling:** Every hash utilizes a unique, deterministic alphabet mapping, adding a layer of obfuscation.
*   **Deterministic & Portable:** Guarantees consistent output for any given input across Python 3.10+ environments.

---

# 🏗 Algorithm Strategy

## 1. 512-Byte State Derivation
*   **1.1 - MDL Derivator:** Generates an initial 512-byte state utilizing Modifier (MDL) layers.
*   **1.2 - Deterministic Shuffle:** Applies a Fisher-Yates shuffle tied strictly to input entropy.
*   **1.3 - Deep Bidirectional Diffusion:** A dual-pass (forward/backward) diffusion layer ensures a full avalanche effect.
*   **1.4 - Jump-Mix Bit Rotation:** Combines non-linear bitwise rotation with dynamic index jumping to break structural patterns.

## 2. 64-Byte Compression
*   **2.1 - Targeted Re-Derivation:** Concentrates the 512-byte state into a 64-byte block.
*   **2.2 - Advanced Dispersion:** Uses chained XOR operations, RNG-driven state jumps, and 4-bit rotations to maximize byte-level entropy.

## 3. Dynamic Base64 Encoding
*   **3.1 - Alphabet Generation:** Shuffles a 64-character pool (0-9, a-z, A-Z, -+) using up to 256 depth cycles.
*   **3.2 - Final Mapping:** Maps compressed bytes to the dynamic alphabet via `byte % len(alphabet)`.

---

# 🚀 Installation

```bash
git clone https://github.com/fyllus/xhash512.git
cd xhash512
pip install .
```

---

# 💻 Usage

```python
from xhash512 import XHash

# Initialize with 3 MDL layers
hasher = XHash(mods=3)
data = b"experimental_seed_2026"

# Generate 512-bit hash
result = hasher.xh512(data)
print(f"Hash: {result.decode()}")
```

---

# 🧪 Development Roadmap

- [x] Modularize `XBase64` entropy engine and `XHash` hash core.
- [x] Implement dynamic shuffle steps based on input length.
- [x] Achieve 0.00% collision rate in 2 bytes(65,536 sequential inputs) sample stress tests.
- [ ] Achieve 0.00% collision rate in 2_000_000 sample(16 bytes) stress tests.
- [ ] Implement a CLI tool for file hashing and benchmarking.
- [ ] Port core derivation logic to C (Python Extension) for high-performance needs.

---

# 📝 Release Notes (v0.3.0)

### Architectural Refactor
*   **Object-Oriented Core:** Transitioned to a robust `XHash` class for better state management and modularity.
*   **Zero-External-RNG:** Replaced `random.Random` with internal deterministic state propagation for 100% mathematical consistency.

### Performance & Security
*   **Vectorized MDLs:** Modifiers now return a triad of values, increasing complexity without linear CPU overhead.
*   **Memory Optimization:** Standardized on `bytearray` for in-place manipulation, significantly reducing memory allocation overhead.
*   **Sub-10ms Processing:** Optimized main loops to maintain high performance in pure Python environments.

### Validation
*   **16-bit Exhaustion:** Passed full 2-byte space exhaustion (65,536 sequential inputs) with 100% unique mapping.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

> **Disclaimer:** This project is for educational purposes. The developer is not responsible for any misuse or security vulnerabilities arising from the use of this experimental software. It has not undergone formal cryptographic auditing. It is intended for research, identification, or personal projects. Do not use it as a replacement for industry standards (like SHA-256/512) in high-security production environments.