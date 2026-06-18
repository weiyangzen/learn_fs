# sources/test-tools/fio/hash.h

## Purpose
Provides small inline hashing utilities copied from Linux-style helpers: multiplicative hashing for integers and pointers plus Bob Jenkins `jhash` for byte buffers.

## Important APIs, Types, and Functions
Defines `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `JHASH_INITVAL`, `__hash_long`, `hash_long`, `__hash_u64`, `hash_ptr`, `rol32`, `__jhash_mix`, `__jhash_final`, and `jhash`. `hash_long()` returns high bits of a multiplicative hash sized by `BITS_PER_LONG`; `hash_ptr()` casts through `uintptr_t`; `jhash()` mixes arbitrary byte keys with a caller-supplied initial value.

## Control Flow
`jhash()` initializes three 32-bit accumulators from length and seed, processes full 12-byte chunks through `__jhash_mix`, then folds the final 0 to 12 bytes through a fallthrough switch and `__jhash_final`. The multiplicative helpers perform constant multiplication and right shifts for hash-table indexing.

## State and Persistence Behavior
No state is stored. Outputs are deterministic for the same input, architecture width, and seed.

## Dependencies and Integration Points
Depends on `arch/arch.h` for `BITS_PER_LONG` and `compiler/compiler.h` for `fio_fallthrough`. Used anywhere fio needs compact hash-table distribution without pulling in a separate library.

## Risks
The 32-bit fallback in `__hash_long()` is intentionally hand-expanded and architecture-sensitive. `jhash()` adds `*k`, `*(k + 4)`, and `*(k + 8)` as single bytes in the full-block loop rather than assembling 32-bit little-endian words, so behavior must be treated as fio's local contract rather than assumed identical to every Jenkins hash variant. These hashes are not cryptographic.

## Test Signals
Good tests pin known hash outputs on 32-bit and 64-bit builds, compare bucket distribution for common keys, and compile with warnings enabled to verify fallthrough annotations.
