# sources/storage-engines/rocksdb/util/bloom_impl.h

Purpose: contains implementation details for RocksDB Bloom-like filters. It provides false-positive-rate math, a current cache-local Bloom implementation optimized for 64-byte cache lines and AVX2 queries, and legacy Bloom implementations kept for reading/building compatible formats.

Important APIs and types: `BloomMath` exposes `StandardFpRate`, `CacheLocalFpRate`, `FingerprintFpRate`, and `IndependentProbabilitySum`. `FastLocalBloomImpl` exposes `EstimatedFpRate`, `ChooseNumProbes`, `AddHash`, `AddHashPrepared`, `PrepareHash`, `HashMayMatch`, and `HashMayMatchPrepared`. `LegacyNoLocalityBloomImpl` provides traditional double-hashing Bloom add/query. `LegacyLocalityBloomImpl<ExtraRotates>` provides cache-line-local legacy add/query and read preparation with configurable cache-line byte size.

Control flow and state: all implementations are stateless static helpers over caller-owned filter bytes. Fast-local add selects a cache line with `FastRange32(h1, len_bytes >> 6)` and sets probe bits within that 512-bit line using repeated multiplication by the 32-bit golden-ratio constant. Query either loops scalar or, under `__AVX2__`, evaluates up to eight probes per vector batch using loads, permutes, blends, masks, and `_mm256_testc_si256`.

Dependencies and integration: depends on `port/port.h` for `PREFETCH`, `rocksdb/slice.h`, `util/hash.h`, and `<immintrin.h>` when AVX2 is available. It integrates below block-based filter policies and is tested through `bloom_test.cc`.

Risks and test signals: fast-local assumes 64-byte cache-line buckets and uses 32-bit fast-range indexing, with comments noting huge-filter accuracy limits and abrupt breakdown at 256GB of cache lines. AVX2 code assumes little-endian layout equivalence. Legacy variants are explicitly marked "DO NOT REUSE" because of speed and accuracy deficiencies. `bloom_test.cc` provides strong schema, FP-rate, corrupt-filter, and Ribbon fallback coverage, but AVX2-specific behavior only runs on AVX2 builds.
