# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/cgen64.c

## Purpose
Implements 64-bit integer (`vlong`) lowering for the 32-bit 386 compiler backend.

## Key Concepts
- Represents 64-bit values as low/high 32-bit register pairs (`OREGPAIR`).
- `hi64v()`, `lo64v()`, `hi64()`, and `lo64()` split constants with endian awareness.
- `loadpair()` and `storepair()` move between memory/scalar nodes and register pairs.
- `biggen()` is a table-driven mini-interpreter for 64-bit operation recipes.
- `cgen64()` handles 64-bit arithmetic, shifts, comparisons, casts, compound assignments, multiply, and increments.
- `testv()` emits boolean tests for 64-bit values.

## Important Behavior
- Table recipes describe how to lower:
  - 64-bit shifts by variable and constant counts,
  - add/subtract with carry/borrow,
  - bitwise operations,
  - comparisons across high/low halves,
  - multiplication through partial products,
  - cast sign/zero extension,
  - pre/post increment/decrement.
- Carefully reserves or evacuates `AX`, `DX`, and `CX` when x86 instructions impose register constraints.
- Supports constant/known-address/hard-address operand classification to choose cheaper code paths.
- `machcap(Z)` enables a path for native 64-bit-style handling tests in this backend.

## Research Notes
This file is a dense table-driven code generator. Correctness depends on preserving low/high half offsets and register-pair ownership across `biggen()` recipes.
