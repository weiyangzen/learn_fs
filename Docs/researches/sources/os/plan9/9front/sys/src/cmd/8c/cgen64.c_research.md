# File Research: sources/os/plan9/9front/sys/src/cmd/8c/cgen64.c

This file implements 64-bit integer operations for the 32-bit 386 compiler backend.

Key responsibilities:
- Represents 64-bit values as register pairs (`OREGPAIR`) or two 32-bit memory words.
- Provides endian-aware `hi64v()`, `lo64v()`, `hi64()`, and `lo64()` helpers.
- Implements `loadpair()` and `storepair()` for moving vlong values between memory, constants, and register pairs.
- Uses a compact table-driven interpreter, `biggen()`, to emit instruction sequences for 64-bit add/sub/and/or/xor, shifts, comparisons, increment/decrement, casts, and multiplication.
- Handles hard-register hazards around `AX`, `DX`, and `CX`.
- `cgen64()` is the main dispatcher for vlong operations and returns whether it handled a node.
- `testv()` emits truth tests for 64-bit expressions.

Integration points:
- Called from `cgen.c`, `sugen()`, and boolean generation.
- Uses 386 instruction emission from `txt.c`, multiplication lowering from `mul.c`, and type/addressability helpers from `gc.h`.
- `machcap()` can choose whether direct 64-bit comparison/test code paths are available.

Risks and invariants:
- The mini bytecode tables are dense and fragile; table opcode mistakes can generate subtly wrong carry, shift, or sign-extension behavior.
- Register-pair lazy allocation requires careful cleanup through `freepair()`/`zapreg()`.
- Some paths temporarily mutate node types and offsets, then restore them.
