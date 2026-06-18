# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/mul.c

Constant-multiply strength-reduction support for ARM `5c`.

Key behavior:
- Searches for short sequences of shifts, adds, and subtracts to replace multiplication by constants.
- Caches generated sequences in `multab`.
- Uses a hint table for constants the generic search misses.
- Recursively builds candidate sequences with `gen1`, `gen2`, and `gen3`.
- `docode` verifies and materializes a compact operation encoding.

Important data:
- `maxmulops = 3` limits replacement sequence length.
- `hintab[]` lists exceptional constants and hand-coded sequences.
- `hintabsize` exposes table size.

Notes:
- Supports later backend code that emits optimized multiply-by-constant instruction sequences instead of `MUL`.
