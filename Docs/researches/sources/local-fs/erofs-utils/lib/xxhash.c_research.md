# File Research: sources/local-fs/erofs-utils/lib/xxhash.c

## Scope

This file provides local xxHash32 and xxHash64 implementations copied/adapted from the Linux kernel and original xxHash project, used by erofs-utils for fast non-cryptographic hashing.

## Public And Internal APIs Covered

- `xxh32()` computes a 32-bit xxHash over a byte buffer with a caller seed.
- `xxh64()` computes a 64-bit xxHash over a byte buffer with a caller seed.
- Internal helpers implement 32-bit and 64-bit rounds, rotate operations, and 64-bit merge rounds.

## Control Flow And Behavior

- `xxh32()` processes 16-byte stripes into four accumulators when enough input is present, handles remaining 4-byte and 1-byte tails, mixes length, and applies the avalanche finalization.
- `xxh64()` processes 32-byte stripes into four 64-bit accumulators, merges them, handles 8-byte, 4-byte, and 1-byte tails, mixes length, and applies the 64-bit avalanche finalization.
- Both functions use unaligned little-endian loads from EROFS helper macros.

## State And Data Structures

- Defines xxHash prime constants as file-static 32-bit and 64-bit constants.

## Dependencies

- Depends on `erofs/defs.h` for fixed-width types and unaligned little-endian load helpers.

## Risks And Invariants

- This is non-cryptographic hashing; callers must not use it for authenticity or collision-resistant identity.
- Correctness depends on little-endian unaligned load helpers matching the xxHash reference byte order.
