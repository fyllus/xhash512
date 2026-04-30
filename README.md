# xHash512

**Version:** 0.3.0-beta (Experimental)
**Author:** fyllus
**License:** MIT

`xHash512` is an experimental non-standard hashing library designed for high-entropy unique identification and obfuscation. It produces a 64-character fixed-length string (512 bits) using a multi-stage process of bidirectional diffusion, non-linear bit rotation, and dynamic alphabet encoding.

> [!WARNING]
> **EXPERIMENTAL PROJECT:** This library is a study on data diffusion and bitwise manipulation. It has not undergone formal cryptographic auditing. Use it for research, identification, or personal projects. **Do not use it as a replacement for audited standards like SHA-256/512 in high-security production environments.**

---

## 🛠 Features

* **Modular Architecture:** Logic separated into `XBase64` (entropy engine) and `xh512` (hash core).
* **Bidirectional Diffusion:** Dual-pass XOR chains ensure a change in one bit ripples through the entire 512-byte internal state.
* **Non-Linearity:** Implements circular bit shifts (ROL) and RNG-based jump mixing to prevent linear algebraic attacks.
* **Dynamic KDF-like Seed:** Replaces standard PBKDF2 with a custom, lightweight Key Derivation logic using dynamic shuffle rounds based on input length.
* **Deterministic & Portable:** Guarantees the same output for the same input across any Python 3.10+ environment.

---

## 🏗 How it Works

The hashing process follows a "Confuse and Diffuse" architecture:

1.  **State Initialization:** A 512-byte internal buffer is created using the input data and length.
2.  **Entropy Engine (`XBase64`):** A custom RNG is initialized using a derived seed, providing high-entropy shuffle parameters.
3.  **Deterministic Shuffle:** A Fisher-Yates shuffle rearranges the buffer based on input-byte positional values.
4.  **Bidirectional Pass:** Information spreads across the buffer in two directions, ensuring a full avalanche effect.
5.  **Bit Rotation & Jump Mix:** A non-linear stage where bytes are XORed with distant neighbors and bit-rotated (3-bit ROL) to destroy patterns.
6.  **Block Compression:** The 512-byte state is compressed into 64 bytes using chained XOR-accumulators and a secondary RNG re-seeded by the diffused state.
7.  **Dynamic Encoding:** The final bytes are mapped to a uniquely shuffled Base64 alphabet, where the shuffle intensity (steps) is determined by the input size.

---

## 🚀 Installation

```bash
git clone [https://github.com/fyllus/xhash512.git](https://github.com/fyllus/xhash512.git)
cd xhash512
pip install .
```

---

## 💻 Usage

```python
from xhash512 import xh512

# Hashing bytes
data = b"experimental_seed_2026"
result = xh512(data)

print(f"Hash: {result.decode()}")
# Output: 64-character high-entropy bytes
```

---

## 🧪 Development Roadmap

- [x] Modularize `XBase64` entropy engine.
- [x] Implement dynamic shuffle steps based on input length.
- [ ] Implement a CLI tool for direct file hashing.
- [ ] Add collision resistance benchmarks (Avalanche/Frequency tests).
- [ ] Port core logic to a C extension for high-performance environments.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### Important Disclaimer
*This project is for educational purposes regarding data diffusion and bitwise manipulation. The developer is not responsible for any security breaches resulting from the use of this experimental software.*
```