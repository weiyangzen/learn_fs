## sources/storage-engines/rocksdb/table/block_based/block_cache.h

Purpose: declares role-specific block-like wrapper types and cache interfaces for block-based table cache entries. The design gives each cached payload a compile-time `CacheEntryRole` and `BlockType` without virtual dispatch overhead.

Important APIs/types: `Block_kData`, `Block_kIndex`, `Block_kFilterPartitionIndex`, `Block_kRangeDeletion`, and `Block_kMetaIndex` derive from `Block`; `Block_kUserDefinedIndex` derives from `BlockContents`; `BlockCreateContext` carries construction settings and provides templated compressed/raw `Create()` plus overloads for each block-like type. `BlockCacheInterface<T>` and `BlockCacheTypedHandle<T>` alias `FullTypedCacheInterface`. `UncacheAggressivenessAdvisor` models when to keep evicting blocks.

Control flow: typed cache users instantiate `BlockCacheInterface<TBlocklike>` with a `BlockCreateContext`. If cached content is compressed, the templated `Create()` decompresses into allocated block contents; otherwise it copies raw bytes. It then dispatches to role-specific overloads and returns memory charge from `ApproximateMemoryUsage()`.

State and persistence behavior: wrapper types do not persist extra data; they annotate cached entries for cache role accounting and helper selection. `BlockCreateContext` carries transient table-reader state. `UncacheAggressivenessAdvisor` maintains useful/not-useful erase counters and stops aggressive uncaching when the observed useful ratio drops below a threshold derived from the option.

Dependencies/integration points: depends on typed cache, `Block`, `BlockType`, filter parsing, table format, compression allocators, and RocksDB cache role options. It is central to block reads, cache warming, secondary cache interaction, and checksum initialization.

Risks: the SFINAE `WithBlocklikeCheck` relies on all block-like types having `kCacheEntryRole`. Wrong `index_value_is_full` or `index_has_first_key` context causes index checksum/protection parsing mismatch. Decompression creation requires `ioptions` and `decompressor` to be valid.

Test signals: `block_test.cc` explicitly creates typed data/index/meta blocks and validates checksum and memory behavior. `block_based_table_reader_test.cc` exercises cache role charging and strict capacity paths.
