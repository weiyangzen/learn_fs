# sources/storage-engines/rocksdb/db/experimental.cc

## Purpose

This file implements APIs in `ROCKSDB_NAMESPACE::experimental`. It has two major areas: thin experimental DB utilities for compaction, manifest checksum retrieval, and offline manifest repair; and a larger experimental SST query-filter framework that serializes table-property filters and builds range-query table filters from them.

The SST query-filter code introduces configurable key-segment extraction, filter input selection, bytewise min/max filters, category/extractor wrappers, collector factories, versioned configuration lookup, and range-time filter evaluation.

## Important APIs, Types, and Functions

- `SuggestCompactRange(DB*, ColumnFamilyHandle*, const Slice*, const Slice*)` validates `db != nullptr` and delegates to `DB::SuggestCompactRange()`.
- `PromoteL0(DB*, ColumnFamilyHandle*, int)` validates `db != nullptr` and delegates to `DB::PromoteL0()`.
- The overload `SuggestCompactRange(DB*, const Slice*, const Slice*)` uses `db->DefaultColumnFamily()` and assumes `db` is non-null before the helper validates it, which is a null-dereference risk.
- `GetFileChecksumsFromCurrentManifest()` locates the current manifest, opens it as an optimized manifest read, iterates records with `FileChecksumRetriever`, and fills `FileChecksumList`.
- `UpdateManifestForFilesState()` uses `OfflineManifestWriter` to recover versions, scans live SST files, opens them through `FileSystem`, compares actual file temperature with manifest temperature, writes replacement `VersionEdit` entries when needed, and logs success/failure.
- `SemiStaticCappedKeySegmentsExtractor<N>` and `DynamicCappedKeySegmentsExtractor` implement `KeySegmentsExtractor` by splitting keys at cumulative byte widths, capping segment ends to short key length, and producing stable extractor ids such as `CappedKeySegmentsExtractor4b8b`.
- `GetFilterInput()` selects the whole key, a segment, or a segment range from a key and extracted segment ends, and returns both selected input and the lead-up prefix before that input.
- `SerializeFilterInput()`, `DeserializeFilterInput()`, and `GetFilterInputSerializedLength()` encode/decode one-byte selector forms for whole key, legacy prefix, user timestamp, column name, first 16 single segments, and selected small segment ranges.
- `CategorySetToUint()` and `UintToCategorySet()` reinterpret category bitsets as `uint64_t` and back.
- `BuiltinSstQueryFilters` defines serialized filter tags for extractor/category wrappers and bytewise min/max filters.
- `SstQueryFilterBuilder` and `SstQueryFilterConfigImpl` are internal polymorphic interfaces for constructing encoded filters.
- `CategoryScopeFilterWrapperBuilder` wraps another builder so it only sees keys from selected extractor categories, and serializes category scope plus one nested filter.
- `BytewiseMinMaxSstQueryFilterConfig` builds a filter recording smallest/largest non-empty selected inputs and a separate empty-input flag; reverse mode inverts min/max interpretation for reverse-ordered segments.
- `SstQueryFilterConfigsManagerImpl` stores versioned named filter configs, creates table-property collector factories, and produces range-query table filters.
- Public factories include `MakeSharedCappedKeySegmentsExtractor()`, `MakeSharedBytewiseMinMaxSQFC()`, `MakeSharedReverseBytewiseMinMaxSQFC()`, and `SstQueryFilterConfigsManager::MakeShared()`.

## Control Flow and State Behavior

Manifest checksum retrieval first resolves `CURRENT` to a manifest path, resets the caller-provided checksum list, creates a `SequentialFileReader`, and scans all manifest log records. Corruption callbacks update the local status if still OK. The function returns retriever status before fetching the checksum list.

`UpdateManifestForFilesState()` recovers the offline manifest, then iterates initialized, non-dropped column families and their levels. For each SST, it builds a table filename and opens it with `Temperature::kUnknown` so the filesystem can search all tiers. If temperature repair is enabled and actual temperature differs from manifest metadata, it deletes and re-adds the file in a `VersionEdit` preserving all other metadata. Non-empty edits are applied through `OfflineManifestWriter::LogAndApply()` with a DB directory handle. Counters track updated files and column families.

The filter-building path starts with versioned `SstQueryFilterConfigs`. A factory creates `MyCollector` for the active version/config name. Each user key is extracted into segments/categories if an extractor exists. Sanity checks enforce category contiguity and selected-input ordering. Builders accumulate min/max state. On `Finish()`, the collector computes exact encoded size, optionally wraps filters with extractor/category metadata, writes schema version `1`, serializes filter counts and lengths, and stores the resulting bytes in user-collected table property `rocksdb.sqfc`.

The range-query read path creates a `RangeQueryFilterReader` capturing inclusive lower and exclusive upper bounds, the current extractor, and the manager's extractor map. For each table, the table-filter lambda looks for `rocksdb.sqfc`, validates schema version, and parses nested filters. Unknown, corrupt, unsupported, or mismatched filters intentionally return `true` so RocksDB reads the table rather than incorrectly filtering it out. A bytewise min/max filter can return `false` when both bounds and recorded table min/max prove no overlap.

Config population requires filtering versions to be contiguous, nonzero, and duplicate-free per version/config name. Factories use a relaxed atomic filtering version; version zero is a special empty configuration. For a requested version, `GetConfigs()` uses the greatest configuration version less than or equal to the active version for that config name.

## Persistence and Encoded Data

The manifest functions directly read and update RocksDB persistent metadata. `UpdateManifestForFilesState()` can append new manifest edits offline, so incorrect metadata preservation would affect DB reopen behavior.

The SST query-filter framework persists encoded filter bytes in table properties under `rocksdb.sqfc`. The encoded format includes a schema byte, varint filter counts/lengths, wrapper tags, extractor ids, category sets, filter input selector bytes, empty-input flags, and min/max selected input values. This is durable per SST and consumed later by range query table filtering.

## Dependencies and Integration Points

The utility portion depends on `DB`, `DBImpl`, manifest helpers, `VersionEdit`, `OfflineManifestWriter`, `VersionSet`/column-family metadata, `FileSystem`, manifest log readers, `FileChecksumRetriever`, and logging.

The query-filter portion depends on experimental public types declared in `rocksdb/experimental.h`, `TablePropertiesCollector`, user-collected table properties, `Slice`, varint coding helpers, `RelaxedAtomic`, unordered maps/sets, and table-filter hooks returned by `TablePropertiesCollectorFactory::Factory`.

Integration points include DB option plumbing for collector factories, range-query code that can use `GetTableFilterForRangeQuery()`, and object lifetime assumptions for captured `Slice` bounds and shared manager/extractor objects.

## Risks and Maintenance Notes

The overload `SuggestCompactRange(DB*, const Slice*, const Slice*)` dereferences `db` before the null check in the three-argument helper. Passing null to that overload can crash instead of returning `InvalidArgument`.

Several selector variants in `GetFilterInput()` (`SelectLegacyKeyPrefix`, `SelectUserTimestamp`, `SelectColumnName`) contain `assert(false)` and return an empty slice. In release builds, malformed or prematurely enabled configs using those selectors could silently degrade to unsafe/no-op behavior.

`CategorySetToUint()` and `UintToCategorySet()` rely on `reinterpret_cast` between category set storage and `uint64_t`. Static size checks help, but aliasing/representation assumptions are still delicate.

The serialized filter format is intentionally permissive on read: corruption or unknown types fall back to "may match." That protects correctness but can hide encoding bugs as lost optimization. Many TODO/FIXME comments call out missing unit tests, unsupported expanded selector cases, legacy/user timestamp/column-name support, filter-length subtleties, and partial-failure reporting in collectors.

`GetTableFilterForRangeQuery()` captures `Slice` objects whose backing buffers must outlive read operations; callers must honor the comment or risk dangling references. Collector sanity checks return corruption if category or segment ordering invariants are violated, so custom extractors must preserve those ordering contracts.

`UpdateManifestForFilesState()` opens every live SST through the filesystem and writes manifest edits offline. Failures midway stop processing; only edits already applied before a later failure persist. Callers should treat this as an administrative repair operation requiring careful DB-closed/offline assumptions from `OfflineManifestWriter`.

## Test Signals

Useful tests for the utility functions include null DB validation, current-manifest checksum extraction over valid and corrupted manifests, temperature repair with files on different filesystem tiers, and no-op repair when manifest temperature already matches.

Useful tests for query filters include capped extractor segment ends for short and long keys, selector serialization/deserialization boundaries, min/max filters for forward and reverse order, empty selected inputs, category scope behavior, corrupt/unknown encoded filters falling back to may-match, collector finish encoding size consistency, version population validation, `SetFilteringVersion()` bounds, and lifetime-safe table-filter use across multiple SST properties.
