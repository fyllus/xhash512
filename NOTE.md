# NOTES

## 0.3.0 Release Notes (Development Stage)

### Core Architectural Shift
*   **Object-Oriented Refactoring**: Transitioned from a procedural approach to a robust `XHash` class structure. This enables better state management, modularity, and the ability to inject or limit modifiers during instantiation.
*   **Zero-External-RNG Policy**: Removed `random.Random` dependencies for core hashing logic to ensure 100% mathematical determinism. Entropy is now managed through high-performance bit-shuffling and internal state propagation.

### Performance & Diffusion Enhancements
*   **MDL Strategy System**: Implemented a dynamic Modifier (MDL) orchestration system.
    *   **Vectorization**: Modifiers now return a triad of values $(x, y, z)$, increasing the complexity of each derivation step without proportional CPU overhead.
    *   **Selective Complexity**: Ability to scale from 1 to 5 MDL functions to balance between extreme speed and cryptographic-grade dispersion.
*   **Bidirectional Diffusion**: Added a dual-pass (forward and backward) diffusion layer. This ensures that a single bit change in the input triggers an "avalanche effect" that propagates through the entire 512-bit state.
*   **Jump-Mix Bit Rotation**: Integrated non-linear bit rotation with dynamic index jumping (`jidx`), preventing differential analysis and linear pattern recognition.

### Performance Optimizations
*   **Memory Efficiency**: Replaced list-based operations with `bytearray` for in-place memory manipulation, significantly reducing overhead
*   **Simplified Token Derivator**: Optimized the main loop to use bitwise XOR and modular arithmetic, cutting down processing time per hash to sub-10ms ranges in Python.

### Validation & Stress Testing
*   **2M Massive Stress Test**: Successfully implemented a "Massive Collision Test" protocol.
    *   **Scope**: Testing up to **2,000,000 unique samples**.
    *   **Input Entropy**: Samples generated using `os.urandom(16)` coupled with a deterministic counter to ensure absolute input uniqueness.
    *   **Status**: Target achievement of **0.00% collision rate** across 2M iterations.
*   **Raw Binary Integrity**: Standardized on binary input streams (`rb`) to preserve data integrity, ensuring characters like `\n` (0x0A) are treated as raw entropy rather than formatting.

### Technical Roadmap
*   Refactor `XBase64` to support dynamic alphabet shuffling based on the internal 512-bit state.
*   Implement `__call__` dunder method in `XHash` for a more Pythonic API usage (e.g., `hasher(data)`).
*   Finalize the `tools.py` suite with the 5 optimized MDL functions.






# STRATEGY

## 1. 512-Byte Derivation (4 Stages)
*   **1.1 - Deterministic Derivator**: Initial 512-byte state generation utilizing MDL (Modifier) layers.
*   **1.2 - Deterministic Shuffle**: Implementation of the Fisher-Yates algorithm tied to input entropy.
*   **1.3 - Deep Bidirectional Diffusion**: Dual-pass diffusion layer ensuring full avalanche effect across the state.
*   **1.4 - Jump-mix with Bit Rotation**: Non-linear bitwise rotation and index jumping to break mathematical linearity.

## 2. 64-Byte Compression
*   **2.1 - Targeted Derivation**: Re-derivation of the 512-byte state into a concentrated 64-byte block using MDL layers.
*   **2.2 - Advanced Dispersion**: Chained XOR operations, RNG-driven jumps, and 4-bit rotations for maximum byte-level entropy.

## 3. Dynamic Base64 Final Phase (62 Chars + "-+")
*   **3.1 - Dynamic Alphabet Generation**: Alphabet shuffling with depth cycles of up to 256 iterations.
*   **3.2 - Final Mapping**: Character selection via `byte % len(alphabet)` mapping for the final output string.

---
# IMPORTANT

## 1. About the Alphabet
*   **1.1 - Generation**: Built using variable `step` cycles and a deterministic `seed`.
*   **1.2 - Nature**: The alphabet is fully dynamic yet strictly deterministic based on the provided seed.
*   **1.3 - Lookup Basis**: The construction follows a structured sequence pool:
    *   `0-9`: '0123456789'
    *   `a-f`: 'abcdef'
    *   `g-z`: 'ghijklmnopqrstuvwxyz'
    *   `special`: '-+'

## 2. Technical Considerations
By processing data through these interconnected stages, the entropy levels become massive. Every component—the dynamic alphabet, the 512-byte state, the 64-byte compressed block, and the final translation—is tightly coupled and extremely sensitive to input variations.

## 3. Expected Result
A unique, high-dispersion 512-bit (64-character) hash sequence.
