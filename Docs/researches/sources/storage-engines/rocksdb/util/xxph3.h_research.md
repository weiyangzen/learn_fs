# sources/storage-engines/rocksdb/util/xxph3.h

## Purpose

This header vendors a preview xxHash v0.7.2 XXH3 implementation into RocksDB as "XXPH3" so RocksDB can keep using the preview algorithm without colliding with standard xxHash symbols. RocksDB customizations force static inline inclusion, set `XXPH_NAMESPACE` to `ROCKSDB_`, enable static-linking-only APIs, include `<cstring>`, remove unused streaming APIs, and alter the zero-length hash behavior.

## Important APIs, types, and functions

The exported surface is the preview 64-bit XXPH3 API: `XXPH3_64bits`, `XXPH3_64bits_withSecret`, `XXPH3_64bits_withSeed`, `XXPH_versionNumber`, `XXPH32_hash_t`, `XXPH64_hash_t`, and `XXPH128_hash_t` for internal 128-bit multiply results. Internal helpers include endian-safe reads (`XXPH_readLE32`, `XXPH_readLE64`), rotations, byte swaps, `XXPH_mult64to128`, `XXPH3_mul128_fold64`, short-key routines for 1-3, 4-8, 9-16, 17-128, and 129-240 byte inputs, and long-key accumulator paths.

## Control flow

Public one-shot hashing dispatches by input length. Inputs up to 16 bytes use specialized scalar mixers, 17-128 bytes mix selected 16-byte chunks, 129-240 bytes run a midsize loop, and larger inputs use a 64-byte stripe accumulator over a 192-byte default secret. Long-key processing accumulates stripes, scrambles accumulator lanes between blocks, mixes accumulator pairs, and finalizes through an avalanche. Vectorized `XXPH3_accumulate_512` and `XXPH3_scrambleAcc` branches support AVX2, SSE2, NEON, VSX, and scalar fallback, selected by preprocessor feature checks.

## State and persistence behavior

The file has no runtime persistence. It defines immutable constants, including prime constants and the 192-byte default secret `kSecret`. Hash results are deterministic for this preview implementation and build target semantics, but comments warn that upstream XXH3 preview versions are not stable for long-term stored values. RocksDB's local fork makes that explicit by renaming the namespace and symbols.

## Dependencies and integration points

The code depends on standard fixed-width integer types when available, compiler intrinsics for vectorization, RocksDB namespace configuration, and `memcpy` for portable unaligned reads. It is consumed by RocksDB hashing code, with `util/hash.cc` calling `XXPH3_64bits` and `XXPH3_64bits_withSeed`. Static inline inclusion avoids exported symbol conflicts, including unity builds.

## Risks

The main correctness risk is hash compatibility: this is not final XXH3, and RocksDB intentionally preserves preview behavior. The RocksDB-specific empty-input change returns a folded hash of the seed/secret instead of zero, so replacing this file with upstream xxHash would silently change results. Other risks are preprocessor portability, vector intrinsic compilation on less common architectures, undefined behavior if callers violate custom-secret size requirements, and poor collision resistance if users supply weak custom secrets.

## Test signals

Relevant signals are hash determinism tests, cross-platform hash-value tests, RocksDB `util/hash.cc` callers, and any persistence or format tests that rely on stable hash values. Build coverage across AVX2/SSE2/NEON/VSX/scalar targets is especially important because much of the implementation is selected at compile time.
