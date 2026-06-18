# sources/storage-engines/rocksdb/table/block_based/filter_policy.cc

## Purpose
Implements RocksDB built-in Bloom-like filter policies, including legacy Bloom, fast local Bloom, Standard128 Ribbon, read-only built-in compatibility, string/object-library construction, metadata decoding, and corruption post-verification hooks.

## Important APIs, Types, And Functions
Anonymous builders/readers include `XXPH3FilterBitsBuilder`, `FastLocalBloomBitsBuilder`, `FastLocalBloomBitsReader`, `Standard128RibbonBitsBuilder`, `Standard128RibbonBitsReader`, `LegacyBloomBitsBuilder`, `LegacyBloomBitsReader`, `AlwaysTrueFilter`, and `AlwaysFalseFilter`. Policy methods include `BloomFilterPolicy::GetBuilderWithContext`, `RibbonFilterPolicy::GetBuilderWithContext`, `BuiltinFilterPolicy::GetBuiltinFilterBitsReader`, `GetBloomBitsReader`, `GetRibbonBitsReader`, `FilterPolicy::CreateFromString`, `NewBloomFilterPolicy`, `NewRibbonFilterPolicy`, and test-only fixed-implementation factories.

## Control Flow
`BloomLikeFilterPolicy` sanitizes bits-per-key, computes millibits/key, whole bits/key, and Ribbon target false-positive rate. Bloom policy chooses legacy Bloom for table format versions before 5 and fast local Bloom otherwise. Ribbon policy chooses Bloom before configured levels or Ribbon for lower/bottom levels. Builders hash keys, de-duplicate adjacent key or prefix hashes, allocate rounded filter storage, write filter bits, append five bytes of metadata, and optionally verify hash-entry checksums and post-verify every saved hash against the constructed filter. Readers inspect the metadata trailer: positive first byte means legacy Bloom, `-1` means new Bloom, `-2` means Ribbon, zero/reserved/invalid encodings return safe fallback readers.

## State And Persistence Behavior
Persistent filter content consists of raw filter bits plus a five-byte built-in metadata trailer. Legacy Bloom stores num probes and num cache lines. Fast local Bloom stores `-1`, subimplementation `0`, probe count/block-size bits, and reserved zero bytes. Standard128 Ribbon stores `-2`, seed, and a 24-bit block count. Runtime state includes cached hash entries, optional cache-reservation handles for construction memory, aggregate rounding balance for `optimize_filters_for_memory`, and atomic mutable `bloom_before_level`.

## Dependencies And Integration Points
Depends on Bloom math/implementations, Ribbon implementations, cache reservation manager, block-based table options, object registry, configuration parsing, logging, sync-point testing, `malloc_usable_size`, and table creation context. Full-filter and partitioned-filter builders use `FilterPolicy::GetBuilderWithContext`; parsed filter blocks use `GetFilterBitsReader` to read existing files across implementation changes.

## Risks And Edge Cases
The implementation must never turn malformed or future filter metadata into false negatives, so reserved or invalid reader formats generally become always-true. Empty or too-short filters become always-false to represent zero added keys, while higher-level readers preserve legacy semantics by treating empty-plugin readers conservatively. Memory-optimized rounding must avoid unexpectedly high false-positive rates. Ribbon construction can fall back to Bloom for too many keys, small filters, cache-charge failure, or seed-solving failure. Corruption-detection code must release hash-entry memory after failures or post-verification.

## Test Signals
Signals include Bloom/Ribbon unit tests elsewhere, full-filter tests in this subset, object-library creation tests, corruption construction sync points, false-positive-rate/space tests, and compatibility tests that read filters written by different built-in implementations.
