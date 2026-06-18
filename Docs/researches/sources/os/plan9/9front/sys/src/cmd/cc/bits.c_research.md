# File Research: sources/os/plan9/9front/sys/src/cmd/cc/bits.c

Purpose: Small bitset operations for compiler analysis state.

Key points:
- Implements `bor`, `band`, `bany`, `beq`, `bnum`, `blsh`, and `bset` over `Bits`.
- `Bits` is an array of `BITS` unsigned long words.
- `bnum` returns the index of the first set bit using `bitno`, and diagnoses empty input.

Dependencies and interactions:
- Uses `Bits`, `BITS`, `zbits`, `diag`, and `bitno` from `cc.h`.
- Used by format checking and other compiler analyses.

Research notes:
- `bnot` is commented out but still declared in `cc.h`, indicating historical or conditionally unused functionality.
