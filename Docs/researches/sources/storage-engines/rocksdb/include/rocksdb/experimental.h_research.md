# sources/storage-engines/rocksdb/include/rocksdb/experimental.h

## Purpose

`experimental.h` gathers APIs that are intentionally not stable. The file covers compaction helpers, manifest metadata update utilities, current-manifest checksum extraction, and a large experimental SST query filtering framework based on key segmentation and versioned filter configurations.

## Important APIs, types, and functions

The simple DB helpers are `SuggestCompactRange`, deprecated `PromoteL0`, `GetFileChecksumsFromCurrentManifest`, and `UpdateManifestForFilesState`. `UpdateManifestForFilesStateOptions` currently controls temperature refresh.

The filtering system centers on `KeySegmentsExtractor`, which maps keys or bounds into `Result { segment_ends, category }`. It defines `KeyCategory`, error pseudo-categories with filter/file/DB scope, `KeyCategorySet`, and `KeyKind` for full keys and iterator bounds. `MakeSharedCappedKeySegmentsExtractor` builds a safer fixed-width segment extractor.

Filter inputs are represented by `FilterInput`, a `std::variant` over `SelectWholeKey`, `SelectKeySegment`, `SelectKeySegmentRange`, and future selectors. `SstQueryFilterConfig` is the non-extensible base for concrete filter schemes. `MakeSharedBytewiseMinMaxSQFC` and `MakeSharedReverseBytewiseMinMaxSQFC` create min/max filters over selected inputs and categories. `SstQueryFilterConfigs` groups filters with an extractor. `SstQueryFilterConfigsManager` stores versioned named configurations and creates `Factory` objects that both collect table properties and produce table filters for range queries.

## Control flow and behavior

Manifest helper calls operate on closed or mostly quiescent DB directories, reading current metadata and writing updated manifest state when file temperature or future metadata is inconsistent. The filtering framework flows from extractor design to SST construction and read filtering. During table building, a factory writes configured filter properties. During reads, `GetTableFilterForRangeQuery` builds a predicate from lower and upper bounds and table properties, returning false for SSTs that definitely cannot match.

The lengthy inline comments are part of the behavioral contract: safe filtering depends on segment maximal prefix, common segment prefix, segment ordering, and category contiguousness properties. Version numbers in `SstQueryFilterConfigsManager` are immutable and gapless, with version 0 reserved for no filters.

## State and persistence

Compaction suggestions and L0 promotion affect LSM layout. Manifest update APIs persist metadata such as file temperatures and checksums. Query filter configs persist indirectly in SST table properties and must stay readable across code versions. Extractor `GetId()` is persistent compatibility state; changing behavior without changing the ID risks incorrect filtering of old files.

## Dependencies and integration points

The header depends on `data_structure`, `db`, `status`, table property collection, `FileSystem`, and checksum list interfaces. It integrates with compaction, manifest editing, `TablePropertiesCollectorFactory`, table filters, column family descriptors, and DB read options. The filtering system is meant to replace or extend older prefix-filter concepts while being version-managed in application code.

## Risks and test signals

The main risk is false-negative filtering: a bad extractor, category assignment, comparator mismatch, or mutated version can cause RocksDB to skip SSTs containing matching keys. The comments document many examples where delimiter handling or short-key categorization breaks correctness. Tests should include property-based extractor ordering checks, range-query filter correctness against full scans, version downgrade/upgrade matrix tests, SSTs written under old configs, unsupported config-name behavior, manifest update on live-changing directories, and checksum extraction from current manifests.
