# sources/storage-engines/rocksdb/util/hash.h

Purpose: public/internal convenience declarations and wrappers for RocksDB hash functions.

Important APIs/types: declares stable `Hash64`, `Hash`, `Hash2x64`, `BijectiveHash2x64`, inverse helpers, `GetSlicePartsNPHash64`, and slice convenience wrappers. Inline `NPHash64` variants currently delegate to `Hash64` unless `ROCKSDB_MODIFY_NPHASH` is defined. `BloomHash()` is the legacy 32-bit Bloom hash. Provides `SliceHasher32` and `SliceNPHasher64` functors plus `Upper32of64`/`Lower32of64`.

Control flow: mostly inline dispatch to out-of-line implementations. `ROCKSDB_MODIFY_NPHASH` intentionally perturbs non-persistent hash output for tests. `GetSliceRangedNPHash()` uses `FastRange64()`.

State and persistence: no owned state except declaration of global function pointer. Comments define persistence contracts: `Hash`/`Hash64` stable, `NPHash64` not for persisted data.

Dependencies and integration: includes `rocksdb/slice.h` and `fastrange.h`. Used broadly by filters, hash containers, memtables, caches, and benchmarks.

Risks: confusing persistent vs non-persistent hash APIs can lead to stored data depending on changeable hashes. `BloomHash()` uses a fixed seed and legacy 32-bit quality. FastRange wrapper requires quality 64-bit hashes.

Test signals: indirect through Bloom/filter tests; no direct test in subset.
