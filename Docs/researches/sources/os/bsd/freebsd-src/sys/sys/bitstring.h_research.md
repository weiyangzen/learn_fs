# File Research: sources/os/bsd/freebsd-src/sys/sys/bitstring.h

## Purpose
`bitstring.h` provides the traditional BSD variable-length bit string API over arrays of `unsigned long`.

## Main Interfaces
- Defines `bitstr_t`, `bitstr_size()`, `bit_alloc()`, and `bit_decl()`.
- Single-bit operations: `bit_test`, `bit_set`, and `bit_clear`.
- Range operations: `bit_ntest`, `bit_nset`, and `bit_nclear`.
- Search operations find first set/clear bit from an offset and first set/clear contiguous area of a requested size.
- `bit_count` counts set bits in a bounded range.
- `bit_foreach` and `bit_foreach_unset` iterate over set or unset bits.

## Implementation Notes
The implementation is inline and word-oriented. Range masks are built from start/stop bit offsets, allowing efficient partial-word handling at both ends and full-word loops in the middle. Area search uses bit manipulation to skip unsuitable runs rather than checking one bit at a time.

## Dependencies and Constraints
Kernel builds use `malloc(..., M_ZERO)` and include `sys/libkern.h`; userland builds use `calloc`. Callers pass bit counts explicitly, and out-of-range search returns `-1`.
