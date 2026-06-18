# sources/storage-engines/rocksdb/util/xxhash.h

## Purpose
`xxhash.h` is RocksDB's vendored xxHash 0.8.1 header with local customizations. It exposes stable public APIs for XXH32, XXH64, XXH3 64-bit, and XXH3 128-bit hashing; optional streaming APIs; canonical big-endian representations; static-linking-only state definitions; and the complete implementation when included with `XXH_IMPLEMENTATION`, `XXH_INLINE_ALL`, or `XXH_PRIVATE_API`.

The RocksDB-specific preamble forces `XXH_STATIC_LINKING_ONLY` and sets `XXH_NAMESPACE` to `ROCKSDB_`, so RocksDB gets access to state structs and advanced APIs while avoiding public symbol collisions with other xxHash users in the same process. It also includes `<utility>` for C++23-and-newer `std::unreachable()` support when the implementation is enabled.

## Important APIs, Types, And Functions
The common public surface defines version macros for 0.8.1, `XXH_versionNumber()`, `XXH_errorcode`, fixed-width hash types `XXH32_hash_t` and `XXH64_hash_t`, canonical byte containers `XXH32_canonical_t`, `XXH64_canonical_t`, and `XXH128_canonical_t`, and 128-bit return type `XXH128_hash_t { low64, high64 }`.

XXH32 APIs include one-shot `XXH32(input, length, seed)`, streaming state APIs `XXH32_createState`, `XXH32_freeState`, `XXH32_copyState`, `XXH32_reset`, `XXH32_update`, `XXH32_digest`, and canonical conversion helpers. The implementation uses four 32-bit accumulator lanes, 16-byte stripes for long inputs, a temporary buffer for streaming tails, and an avalanche finalizer.

XXH64 APIs mirror the XXH32 shape with 64-bit seeds and results. The implementation uses four 64-bit lanes, 32-byte stripes, merge rounds for long inputs, and a 64-bit avalanche finalizer.

XXH3 APIs include one-shot `XXH3_64bits`, `XXH3_64bits_withSeed`, `XXH3_64bits_withSecret`, `XXH3_64bits_withSecretandSeed`, and the corresponding `XXH3_128bits` variants plus alias `XXH128(data, len, seed)`. Streaming uses shared `XXH3_state_t` with reset/update/digest variants for both 64-bit and 128-bit output. Advanced APIs include `XXH3_generateSecret()` and `XXH3_generateSecret_fromSeed()`.

The static-linking section exposes `XXH32_state_s`, `XXH64_state_s`, and `XXH3_state_s`. These are explicitly unstable internal layouts. `XXH3_state_s` is 64-byte aligned and contains accumulator lanes, a generated custom secret buffer, a 256-byte input buffer, stripe counters, total length, seed flags, secret limits, and an optional external secret pointer.

## Control Flow
The header has two major compile-time phases. First, it declares the stable public API unless already included. Second, when static linking or implementation macros are active, it exposes internal state and then compiles the implementation behind a one-time implementation guard.

Public one-shot control flow depends on input length. `XXH32()` chooses an aligned or unaligned path when enabled, processes full 16-byte blocks through four accumulator lanes, then finalizes the remaining 0-15 bytes. `XXH64()` follows the same pattern with 32-byte blocks and 0-31 byte finalization.

`XXH3_64bits_internal()` and `XXH3_128bits_internal()` choose specialized short-input routines for `len <= 16`, mid-size routines for `17..128`, another mid-size path for `129..240`, and long-input accumulation for larger data. Long-input XXH3 initializes eight 64-bit accumulators, consumes 64-byte stripes with a secret-dependent multiply/add routine, scrambles accumulators at block boundaries, handles the last stripe specially, and merges accumulator pairs into final 64-bit or 128-bit hashes.

Streaming control flow buffers small updates until enough bytes exist to process. XXH32 and XXH64 fill their internal tail buffers, process full stripes, and leave remaining bytes buffered. XXH3 uses a 256-byte buffer and stripe/block counters; for large updates it may consume complete secret blocks directly, scramble between blocks, and preserve a previous stripe so digest can include the required final-stripe treatment. Digest functions work on the current state without consuming it, so callers can update again after digest.

## State And Persistence Behavior
The hash functions are deterministic and non-cryptographic. One-shot APIs are effectively stateless from the caller's perspective. Streaming APIs require caller-owned state allocated through the matching create/free functions or stack-allocated static-linking structs initialized and reset as documented.

No on-disk persistence happens in this header, but hash outputs are used by RocksDB persisted formats such as table block checksums and WAL/log checksums. That raises compatibility stakes: changing algorithm version, namespace behavior, endian canonicalization, or RocksDB's special use of XXH3 would affect data verification across versions. The header's canonical helpers serialize hash values in big-endian order for portable storage or network representations.

External secret streaming mode stores a pointer, not a copy; callers must keep the secret alive for the whole streaming session. Seeded XXH3 streaming can generate and store a custom secret in state. `XXH3_createState()` uses custom aligned allocation because XXH3 state must meet SIMD alignment requirements.

## Dependencies
The public declaration layer uses standard headers such as `<stddef.h>`, `<stdint.h>` where available, and compiler attributes for purity, malloc-like allocation, noescape, and fallthrough annotations. The implementation adds `<stdlib.h>`, `<string.h>`, `<limits.h>`, optional `<assert.h>`, platform intrinsics (`<immintrin.h>`, `<emmintrin.h>`, ARM NEON/SVE headers, VSX/ZVector headers, or MSVC intrinsics), endian/unaligned access helpers, and compiler builtins for rotates, byte swaps, prefetch, branch prediction, and unreachable paths.

Key compile-time tuning macros include `XXH_FORCE_MEMORY_ACCESS`, `XXH_SIZE_OPT`, `XXH_FORCE_ALIGN_CHECK`, `XXH_NO_INLINE_HINTS`, `XXH_NO_STREAM`, `XXH_NO_LONG_LONG`, `XXH_NO_XXH3`, `XXH_VECTOR`, and `XXH_ACC_ALIGN`.

## Integration Points
RocksDB includes this header anywhere it needs the current stable xxHash implementation. `table/format.cc` uses `XXH32`, `XXH64`, and `XXH3_64bits` for built-in block checksums; for `kXXH3`, RocksDB applies custom last-byte handling to avoid streaming overhead for compression-type extension. `db/log_reader.cc` uses `XXH3_createState`, reset, update, digest, and free to checksum full and fragmented WAL records. `db/write_batch.cc` uses `XXH3_64bits` for write-batch protection. `utilities/fault_injection_fs.cc`, DB stress checksum generators, db_bench checksum benchmarks, table reader diagnostics, options parsing, and Java checksum configuration all connect to the same checksum family.

RocksDB also retains `util/xxph3.h`, a preview XXH3 variant used by `util/hash.cc` for existing non-persisted hash behavior, while this header is the stable 0.8.1 xxHash surface used for current checksum and hashing APIs.

## Risks And Edge Cases
This is performance-sensitive, platform-sensitive third-party code. Risk areas include unaligned memory access mode, endian detection, SIMD target selection, strict 64-byte alignment for XXH3 state, and macro consistency between the compiled implementation unit and all include sites. Misusing static-linking state layouts, allocating `XXH3_state_t` with ordinary `malloc`/`new`, or freeing aligned states with the wrong function can break alignment or memory ownership assumptions.

Several APIs rely on documented preconditions for speed: input must be readable unless length is zero, custom secrets must be at least `XXH3_SECRET_SIZE_MIN`, and external secrets must outlive streaming sessions. In many implementation paths these are asserted rather than fully checked, so production builds may not guard every misuse. The code is explicitly non-cryptographic; unseeded XXH3 is not intended to resist adversarial collision construction.

For RocksDB specifically, checksum compatibility is the main operational risk. `kXXH3` is a persisted checksum type supported since RocksDB 6.27 and now appears as a default in table options. Any update to this vendored header needs compatibility tests that prove persisted block/WAL checksums still verify or a deliberate format/version transition.

## Test Signals
Relevant test signals include table checksum tests for `kxxHash`, `kxxHash64`, and `kXXH3`; `util/hash_test.cc` coverage around XXH3 size thresholds and bijective helpers; WAL/log tests that exercise one-shot and streaming XXH3 paths; DB key-value checksum tests comparing against `XXH3_64bits`; fault-injection filesystem checksum checks; DB stress custom checksum generators using XXH64 streaming; and db_bench checksum benchmarks for `xxhash`, `xxhash64`, and `xxh3`. Cross-platform CI should include little-endian x86_64, ARM/NEON, and at least one no-SIMD or scalar configuration when possible.
