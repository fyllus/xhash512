# xHash512

**Version:** 0.1.0-alpha (Experimental)  
**Author:** hazzorgod  
**License:** MIT

`xHash512` is an experimental non-standard hashing library designed for high-entropy unique identification and obfuscation. It produces a 64-character fixed-length string (512 bits) using a multi-stage process of diffusion, bitwise rotation, and dynamic encoding.

> [!WARNING]  
> **HIGHLY EXPERIMENTAL:** This library is in its early stages (v0.1.0). It has not undergone formal cryptographic auditing. Use it for personal projects, research, or identification purposes. **Do not use it for sensitive industrial-grade security or as a replacement for audited standards like SHA-256/SHA-512 in production environments.**

---

## 🛠 Features

* **Fixed Output:** Always returns a 64-character string.
* **Bidirectional Diffusion:** Multi-pass XOR chains (forward and backward) to ensure a strong avalanche effect.
* **Non-Linearity:** Implements circular bit shifts (ROL) and RNG-based jump mixing to break linear algebraic relationships.
* **Dynamic Alphabet:** Uses **PBKDF2 (100,000 iterations)** to derive a unique character mapping for each hash, significantly increasing the cost of brute-force analysis.
* **Zero Bias:** Base64-compliant alphabet (64 chars) ensures perfect statistical distribution (no modulo bias).

---

## 🏗 How it Works

The hashing process follows a "Confuse and Diffuse" architecture:

1.  **State Initialization:** Creates a 512-byte internal buffer seeded by the input data and its length.
2.  **Deterministic Shuffle:** A Fisher-Yates shuffle rearranges the buffer based on input-byte positional values.
3.  **Bidirectional Pass:** Information is spread across the buffer in two directions, ensuring that a change in the first byte of input affects the entire output.
4.  **Bit Rotation & Jump Mix:** A non-linear stage where bytes are XORed with distant neighbors (jumps) and bit-rotated to destroy simple patterns.
5.  **Compression:** The 512-byte state is compressed into 64 raw bytes using a chained XOR-accumulator with a local RNG.
6.  **Alphabet Derivation:** The final 64 bytes are used to generate a unique, shuffled alphabet via PBKDF2 with 100k rounds.
7.  **Mapping:** The compressed bytes are mapped to the dynamic alphabet to produce the final string.

---

## 🚀 Installation (Planned)

```bash
# Not yet available on PyPI
git clone https://github.com/fyllus/xhash512.git
cd xhash512
pip install .
```

---

## 💻 Usage

```python
from xhash512 import xh512

# Simple hashing
data = b"Hello, There"
result = xh512(data)

print(f"Hash: {result}")
# Output: A 64-character high-entropy string
```

---

## 🧪 Development Roadmap

- [ ] Optimize PBKDF2 performance for mobile environments.
- [ ] Implement a CLI tool for file hashing.
- [ ] Add comprehensive collision resistance benchmarks (Avalanche test).
- [ ] Port the core logic to C/Rust as a Python extension for maximum speed.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### Important Disclaimer
*The developer is not responsible for any data loss or security breaches resulting from the use of this experimental software. This is a learning-focused project on data diffusion and bitwise manipulation.*