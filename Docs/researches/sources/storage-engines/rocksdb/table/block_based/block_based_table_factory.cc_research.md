# sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.cc

## Purpose
`block_based_table_factory.cc` implements RocksDB's `BlockBasedTableFactory`, the `TableFactory` backend that creates block-based SST readers and builders, owns configuration parsing/printing for `BlockBasedTableOptions`, validates cross-option compatibility, and provides shared per-factory state such as table-reader cache memory reservations and tail prefetch history. This is the option and construction entry point that links public table options to `BlockBasedTable::Open()` and `BlockBasedTableBuilder`.

## Important APIs, Types, And Functions
`TailPrefetchStats::RecordEffectiveSize()` stores recent effective tail-read byte counts in a mutex-protected ring buffer of 32 samples. `TailPrefetchStats::GetSuggestedPrefetchSize()` sorts the collected samples, chooses the largest candidate whose estimated wasted bytes are no more than one eighth of total bytes read, and caps the result at 512 KiB. A return value of `0` means no samples are available.

The static option metadata includes enum maps for `PinningTier`, `BlockBasedTableOptions::IndexType`, `BlockSearchType`, `DataBlockIndexType`, `IndexShorteningMode`, and `PrepopulateBlockCache`. `metadata_cache_options_type_info` and `block_based_table_type_info.info` describe all registered option names, offsets, option kinds, verification behavior, serialization flags, and custom parsers. Notable custom behavior includes dynamic cache construction through `Cache::CreateFromString()`, custom/shared pointer loading for policies/factories, and a compatibility parser for the historical `read_amp_bytes_per_bit` OPTIONS-file bug that reads a `uint64_t` string into a `uint32_t` field.

`BlockBasedTableFactory::BlockBasedTableFactory()` copies the incoming `BlockBasedTableOptions`, initializes defaults/sanitization, registers option metadata, and creates a `ConcurrentCacheReservationManager` for `CacheEntryRole::kBlockBasedTableReader` when block cache exists and table-reader memory charging is enabled.

`InitializeOptions()` installs default `FlushBlockBySizePolicyFactory`, chooses/clears the block cache depending on `no_block_cache`, creates the default 32 MiB `HyperClockCache` when no cache is supplied, clamps invalid block-size deviation and restart intervals, forces hash index restart interval to `1`, disables partitioned filters without two-level index search, resolves fallback cache-usage charging decisions, and raises too-old writable block-based table format versions to the minimum supported write version except for special test allowances.

`CheckCacheOptionCompatibility()` is a local helper that prevents regular block cache and persistent cache from sharing an underlying key space. It inserts a process-unique sentinel into both caches and then verifies each lookup returns the expected marker, returning `InvalidArgument` for overlapping caches and `Corruption` for unexpected mutation.

`NewTableReader()` forwards table-reader construction to `BlockBasedTable::Open()` with the sanitized options, immutable options, env options, comparator, file reader, file size, tail size, compression manager, filter-skip flag, level/lifetime metadata, direct prefetch flag, shared tail prefetch stats, block-cache tracer, L0 metadata pin sizing, DB session/file identity, persisted timestamp flag, and `avoid_shared_metadata_cache`.

`NewTableBuilder()` constructs a `BlockBasedTableBuilder` with the factory's options and the supplied writable file. `ValidateOptions()` checks the table option matrix against DB/column-family options. `GetPrintableOptions()` serializes a human-readable option dump including nested cache options. `GetOptionsPtr()` exposes the block cache option pointer unless block cache is disabled. `ParseOption()` wraps base parsing and keeps legacy escaped string behavior for named custom options. `GetBlockBasedTableOptionsFromString()`, `GetBlockBasedTableOptionsFromMap()`, `NewBlockBasedTableFactory()`, and `UserDefinedIndexFactory::CreateFromString()` provide public convenience/configuration hooks.

The file also defines property-name and metadata-block constants such as `BlockBasedTablePropertyNames::kIndexType`, `kHashIndexPrefixesBlock`, `kHashIndexPrefixesMetadataBlock`, `kPropTrue`, and `kPropFalse`.

## Control Flow
Factory construction follows a deterministic sequence: copy options, normalize them in `InitializeOptions()`, register the option metadata table, then optionally create shared table-reader memory reservation state from cache usage options. Later `PrepareOptions()` reruns `InitializeOptions()` before delegating to `TableFactory::PrepareOptions()`.

Reader creation is a thin but critical bridge: `NewTableReader()` does not parse table contents itself; it packages all validated options and shared factory state into `BlockBasedTable::Open()`. Builder creation is similarly direct, returning a raw `TableBuilder*` allocated as `BlockBasedTableBuilder`.

Validation is a long fail-fast chain. It first checks indexing prerequisites, cache/pinning requirements, and format-version support. It then evaluates compression compatibility, including custom `CompressionManager` restrictions for format versions below 7 and `block_align` incompatibility with compression. After physical size/alignment checks, it validates data-block hash-index utilization, user-defined index constraints, unordered-write merge constraints, cache-entry memory charging support, blob-cache relationships, cache key-space compatibility, checksum enum serialization, and finally the base `TableFactory` validation.

Option parsing flows through RocksDB's configurable-option system. The static `OptionTypeInfo` table maps strings to struct offsets and parsers, `ConfigureFromMap()` is driven by that table through the inherited configurable interface, and the convenience functions either parse a semicolon/string map or map directly before copying the factory's resulting `BlockBasedTableOptions` back to the caller.

## State And Persistence Behavior
`BlockBasedTableFactory` owns a copy of `BlockBasedTableOptions`; initialization mutates that copy to safe defaults and compatibility-preserving values. Cloned factories share `SharedState`, so `TailPrefetchStats` samples and the table-reader cache reservation manager are shared across clones rather than reset on every clone.

`TailPrefetchStats` is in-memory runtime state only. It is protected by `port::Mutex`, records at most 32 recent tail effective sizes, and does not persist to OPTIONS or table files. It influences future opens through `BlockBasedTable::Open()` receiving `tail_prefetch_stats`.

The option metadata controls persistence of table options in configuration strings and OPTIONS files. Fields with `kDontSerialize` or `kCompareNever`, such as cache object pointers, are intentionally excluded from serialized equality/OPTIONS behavior. Deprecated fields remain registered so older option strings can be parsed or ignored in a controlled way.

## Dependencies And Integration Points
This implementation depends on the cache subsystem (`Cache`, cache entry roles, `CacheReservationManager`), RocksDB option/configuration helpers, block-based table reader/builder types, filter/flush/user-defined-index extension points, compression manager compatibility checks, string parsing utilities, and table format constants.

It integrates upward with public APIs through `NewBlockBasedTableFactory()`, `GetBlockBasedTableOptionsFromString()`, `GetBlockBasedTableOptionsFromMap()`, and the `TableFactory` virtual interface. It integrates downward with `BlockBasedTable::Open()` for SST reads and `BlockBasedTableBuilder` for SST writes. It also integrates with cache tracing, metadata cache charging, persistent cache, blob cache memory charging, custom object loading, and user-defined indexes.

## Risks And Edge Cases
Several options are silently normalized rather than rejected during initialization, including invalid restart intervals, invalid block size deviation, hash-index restart interval incompatibility, and partitioned filters without partitioned indexes. This preserves historical behavior but can hide user configuration mistakes until option printing or validation is inspected.

The static option table marks many options mutable while the comment documents an unresolved read/write race for `SetOptions()` on block-based table option fields, especially pointer or larger fields. Callers relying on runtime mutation need to account for this known concurrency risk.

`CheckCacheOptionCompatibility()` intentionally mutates caches with a sentinel to detect shared key spaces. It uses a process-lifetime unique cache key, but any cache implementation with surprising insert/lookup semantics can cause validation failures or corruption statuses.

Compression and format-version validation is sensitive: custom compression managers require format-version support for storing the manager name; `block_align` conflicts with any enabled compression; and non-built-in compression types are rejected when using built-in-compatible compression managers. Tests need to cover both default and custom manager paths.

User-defined index support has explicit restrictions: no parallel compression, no primary UDI with two-level index or partitioned filters, and `use_udi_as_primary_index` requires a configured factory. These constraints protect layouts that the UDI wrapper cannot represent.

Cache-entry charging validation only supports a specific role set, and blob-cache charging has additional capacity and identity restrictions relative to the block cache. Misconfiguration returns `InvalidArgument`.

## Test Signals
Useful test coverage should include default option initialization, no-block-cache behavior, default HyperClockCache installation, option string/map parsing including deprecated or legacy `read_amp_bytes_per_bit` values, printable option output, and validation failures for hash index without prefix extractor, interpolation search with a non-bytewise comparator, cache-index options without block cache, unsupported format versions, `block_align` with compression, non-power-of-two alignments, invalid hash-table utilization ratio, UDI incompatibilities, and blob-cache charging constraints.

Cache compatibility tests should use distinct caches, intentionally shared/wrapped caches, and persistent cache implementations to verify `CheckCacheOptionCompatibility()`. Tail prefetch tests should exercise no-sample return, ring-buffer wraparound, sorted sample selection under the one-eighth-waste rule, and the 512 KiB cap. Reader/builder integration tests should verify `NewTableReader()` passes tail prefetch and cache reservation shared state into `BlockBasedTable::Open()` and that `Clone()` preserves shared state.
