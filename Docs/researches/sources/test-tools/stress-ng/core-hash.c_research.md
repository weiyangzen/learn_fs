# sources/test-tools/stress-ng/core-hash.c

## Purpose

This file implements a collection of non-cryptographic hash algorithms and a small chained hash table used by stress-ng utilities. The hashes support stressor workloads, filename truncation, process-name scrambling, machine-id derivation, warn-once keys, and algorithm benchmarking.

## Important APIs, Types, And Functions

Hash functions include Jenkins, PJW, DJB2a, FNV-1a, SDBM, Exim nhash, Murmur3 32-bit, CRC32C, Adler32, multiply/add variants, K&R, Coffin byte and 32-bit endian variants, lose-lose, Knuth, x17, mid5, mulxror64/32, xorror64/32, Sedgwick, and Sobel. The CRC32C implementation uses a static 256-entry lookup table. Murmur3 uses `stress_hash_murmur_32_scramble`.

The hash table API is `stress_hash_create`, `stress_hash_add`, `stress_hash_get`, and `stress_hash_delete`. `HASH_STR` stores the string payload immediately after a `stress_hash_t` node, and buckets are selected with SDBM modulo table size.

## Control Flow

Most hash functions are straight-line loops over nul-terminated strings or fixed lengths, using shim rotations and `memcpy` for unaligned word loads. `stress_hash_add` validates the table and string, checks for an existing bucket entry, allocates a combined node/string block, prepends it to the bucket, and copies the string. `stress_hash_get` computes the same bucket and scans the linked list. `stress_hash_delete` walks each bucket and frees every node.

## State And Persistence Behavior

The hash functions are stateless and deterministic. The hash table persists in heap allocations owned by the caller until `stress_hash_delete`. Entries are unique by exact `strcmp` within a table. The implementation is not internally synchronized; callers must serialize shared use.

## Dependencies And Integration Points

This module depends on core attributes, builtin shims, pragma unroll macros, rotations, and allocation. It is used by filesystem temp-name truncation, helper process-name scrambling, warn-once hashing, machine ID construction, and likely stressor-specific hash tests.

## Risks And Test Signals

These are non-cryptographic hashes; callers must not use them for security. Some functions accept `len` but still stop at nul bytes, while others use fixed-length block loads, so caller expectations matter. Word-load variants must remain safe on unaligned architectures via `shim_memcpy`. Test signals include stable known-vector outputs, empty-string behavior, endian-specific Coffin variants, table duplicate suppression, collision-chain lookup, zero-sized table rejection, and leak-free deletion.
