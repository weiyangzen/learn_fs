# sources/storage-engines/rocksdb/db/db_table_properties_test.cc

## Purpose

This file tests reading, validating, and interpreting RocksDB table properties. It covers all-table and by-level property retrieval, in-range property queries with and without user-defined timestamps, table identity properties, collector factory behavior, deletion-triggered compaction metadata, sequence-number properties, host identifiers, and compression display-name parsing.

## Important APIs, Types, And Functions

- `VerifyTableProperties` calls `DB::GetPropertiesOfAllTables`, validates unique `num_entries`, total entries, and SST unique IDs.
- `ParseCompressionDisplayNameManager` is a custom `CompressionManagerWrapper` used to test custom compression display names and object registry lookup.
- `DBTablePropertiesTest` is parameterized by compaction style for deletion-triggered compaction tests.
- `DBTablePropertiesInRangeTest` is parameterized by user-defined timestamp enablement and wraps `Put`, `Get`, and `GetPropertiesOfTablesInRange` with timestamp-aware ranges.
- APIs under test include `GetPropertiesOfAllTables`, `GetPropertiesOfTablesByLevel`, `GetPropertiesOfTablesInRange`, table-property collector factory creation, `NewCompactOnDeletionCollectorFactory`, `ParseCompressionNameForDisplay`, and DB identity/session/host property accessors.

## Control Flow

`GetPropertiesOfAllTablesTest` creates four tables with different entry counts, records the DB session id, then tests property retrieval when no table readers are cached, when some readers are cached, and when all are cached. It corrupts a table properties block by mutating the stored session id and verifies corruption is reported both by direct property reads and through table reader access on `Get`.

`InvalidReportedAsCorruption` injects invalid properties-block data through SyncPoint and expects flush to return corruption. `CreateOnDeletionCollectorFactory` parses collector factory strings with default, window/deletion-trigger, and deletion-ratio settings. `GetPropertiesOfTablesByLevelTest` builds a multi-level LSM and checks each returned per-level collection size against `ColumnFamilyMetaData`.

`DBTablePropertiesInRangeTest` builds a multi-level LSM and queries all, empty, middle, and random key ranges. When timestamps are enabled, it uses `MaybeAddTimestampsToRange` and comparator timestamp size to verify file overlap against user-key ranges with appended timestamps.

Column-family, DB identifier, and host tests flush per-CF tables and verify table properties preserve `column_family_name`, `column_family_id`, `db_id`, `db_session_id`, and `db_host_id`. `FactoryReturnsNull` alternates a custom collector factory between returning a collector and `nullptr`, across block-based and plain table factories, and verifies one table has the user property and one does not.

Deletion-triggered compaction tests add `CompactOnDeletionCollectorFactory`, create tombstone-heavy files, and verify files are marked for compaction by count-window and ratio-based policies under level and universal compaction. `KeyLargestSmallestSeqno` checks sequence-number table properties before and after bottommost compaction. `ParseCompressionNameForDisplay` exhaustively validates old/new compression strings, standard/custom/reserved hex values, registry-backed custom manager names, disabled compression markers, future fields, and malformed inputs.

## State And Persistence Behavior

The tests create real SST files and rely on table properties persisted in meta blocks. Reopens and table-cache erasure force direct file property reads versus cached-reader reads. Corruption is written to the SST file and then undone for reuse. LSM-building tests pause background work after compaction reaches useful L0/L1/L2 shapes. Deletion-triggered compaction persists collector-derived metadata that causes subsequent compaction scheduling.

## Dependencies And Integration Points

The file integrates with block-based and plain table formats, meta block parsing, table property collectors, object registry, advanced compression managers, DB identity/session/host metadata, timestamp-aware comparators, live-file metadata, compaction reason reporting, statistics tickers for marked compaction bytes, and SyncPoint injection in table building/loading.

## Risks And Edge Cases

Property retrieval must work with and without table readers in cache. Range overlap logic is comparator-sensitive, especially with user-defined timestamps. Corruption tests assume the session id is present in table properties and that mutating one byte causes checksum failure. Deletion-triggered compaction relies on tombstones not being dropped during flush, so setup adds lower-level files. Compression display parsing is intentionally broad and can fail when serialization format or compatibility names change.

## Test Signals

Signals include table property collection sizes, unique IDs, entry sums, corruption statuses, per-level collection counts, range overlap validation against live-file metadata, CF/DB/host property equality, user-collected property presence/absence, compaction listener reasons, `COMPACT_*_BYTES_MARKED` tickers, key sequence-number fields, and exact display-name strings for compression parsing.
