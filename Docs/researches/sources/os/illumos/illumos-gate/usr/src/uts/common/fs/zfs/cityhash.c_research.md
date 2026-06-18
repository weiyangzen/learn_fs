# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/cityhash.c

## Scope

Provides a compact CityHash-derived 64-bit hash helper for four 64-bit words.

Read completely: 63 lines.

## Main APIs

- `cityhash4(uint64_t w1, uint64_t w2, uint64_t w3, uint64_t w4)` returns a 64-bit hash over four words.

## Implementation

The file defines two CityHash constants, a rotate helper, `cityhash_helper()` mixing function, and `cityhash4()`. `rotate()` explicitly avoids shifting by 64 when the shift value is zero.

## Dependencies

Depends only on `sys/cityhash.h` and fixed-width integer behavior.

## Invariants And Risks

- This is a non-cryptographic hash.
- Correctness depends on unsigned 64-bit overflow semantics.
- The implementation is intentionally specialized to four input words rather than a general byte-string CityHash API.
