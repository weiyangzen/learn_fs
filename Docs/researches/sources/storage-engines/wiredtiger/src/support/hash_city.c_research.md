# sources/storage-engines/wiredtiger/src/support/hash_city.c

## Purpose
`hash_city.c` embeds WiredTiger's wrapper around Google's CityHash64 implementation. It provides a fast, deterministic 64-bit hash for byte strings and is used by support data structures such as the internal hash map.

## Important APIs, Types, and Functions
The public WiredTiger-facing API is `__wt_hash_city64(const void *s, size_t len)`, which returns `CityHash64(s, len)`. Internal helpers include the `uint128` pair structure, `UNALIGNED_LOAD64`, `UNALIGNED_LOAD32`, endian-normalizing `Fetch64` and `Fetch32`, `Hash128to64`, `Rotate`, `RotateByAtLeast1`, `ShiftMix`, `HashLen16`, and length-specialized hash routines for `0..16`, `17..32`, and `33..64` byte ranges. Longer inputs use `WeakHashLen32WithSeeds` and a 64-byte chunk loop.

## Control Flow
The hash path branches by input length. Short inputs mix one or more fetched words with CityHash constants. Medium inputs combine front, middle, and tail words. Inputs longer than 64 bytes seed state from the tail, then iterate over 64-byte chunks while rotating and mixing `x`, `y`, `z`, `v`, and `w`, and finally collapse the state through nested `HashLen16` calls.

## State and Persistence Behavior
The implementation is stateless. It uses compile-time constants `k0` through `k3` and stack-local state only. There is no allocation, locking, or persistence.

## Dependencies and Integration Points
The file includes `wt_internal.h` for basic types and WiredTiger byte-swap fallbacks. Big-endian builds map native loads through platform byte-swap routines or WiredTiger byte-swap helpers so the hash result follows the expected byte order. `hash_map.c` uses `__wt_hash_city64` to choose buckets.

## Risks
CityHash64 is not a cryptographic hash and should not be used where adversarial collision resistance is required. Determinism across architectures depends on the endian conversion branches staying correct. Callers must pass a valid memory range of at least `len` bytes; the function deliberately performs unaligned fixed-width loads near both ends of the buffer for performance. Because this is third-party algorithm code, local style refactors can accidentally change hash compatibility.

## Test Signals
Golden-vector tests should cover lengths 0, 1, 3, 4, 8, 16, 17, 32, 33, 64, 65, and multi-block inputs. Cross-platform tests should compare little- and big-endian outputs for the same byte sequence. Hash-map tests indirectly exercise distribution and bucket selection, but direct deterministic vectors are the strongest signal against accidental algorithm drift.
