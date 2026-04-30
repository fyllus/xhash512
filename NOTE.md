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