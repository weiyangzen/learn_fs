# sources/storage-engines/pebble/table_stats_test.go

## Purpose
This test file validates the behavior implemented by `table_stats.go`. It covers asynchronous table-stat collection, datadriven database mutations, waiting for initial and pending stats, range deletion/range-key deletion span merging, and metric stability after reopening a database with table and blob compression properties.

## Important APIs, Types, and Functions
The exported test functions are `TestTableStats`, `TestTableRangeDeletionIter`, and `TestStatsAfterReopen`. `TestTableStats` creates an in-memory DB with automatic compactions disabled, a test comparer, minimum supported format, a custom `TableStatsLoaded` listener, and a test logger. It delegates most operations to existing datadriven helpers including `runDBDefineCmd`, `runBatchDefineCmd`, `runBuildCmd`, `runIngestCmd`, `runWaitForTableStatsCmd`, `runCompactCmd`, `runMetadataCommand`, `runSSTablePropertiesCmd`, and `runIngestAndExciseCmd`.

`TestTableRangeDeletionIter` builds raw SSTables with `sstable.NewRawWriter`, encodes `keyspan.ParseSpan` input, synthesizes `manifest.TableMetadata` bounds from writer metadata, and opens the resulting SSTable to call `newCombinedDeletionKeyspanIter`. `TestStatsAfterReopen` uses randomized options and workload generation to compare JSON-rendered table and blob compression metrics before close and after reopen plus `waitTableStats`.

## Control Flow
`TestTableStats` drives `testdata/table_stats` commands. `define` recreates a DB from a datadriven description and returns current version text. `disable` and `enable` toggle `DisableTableStats`, with enable calling `maybeCollectTableStatsLocked`. Mutation commands write batches, flush, build/ingest SSTables, ingest-and-excise, or compact ranges, returning LSM or error text. Wait commands block on `d.mu.tableStats.cond` until pending stats or initial loading complete. Metadata and property commands inspect current-version SSTable state.

`TestTableRangeDeletionIter` has a two-phase flow: `build` creates `tmp.sst` in memory from text spans and records bounds on a manifest metadata object; `spans` reopens the table, constructs the combined deletion iterator, and prints every merged span or `(none)`. This directly tests the span merge/defragmentation semantics that feed range deletion byte estimates and wide tombstone discovery.

`TestStatsAfterReopen` constructs many flushed SSTables with random keys/values, occasionally compacts random ranges, then snapshots metrics. After close and reopen, it waits for asynchronous stats loading and asserts that table/blob compression metrics match exactly. The workload forces many small tables by using small block and target file sizes and raises thresholds to avoid stop-write interference.

## State and Persistence Behavior
The tests use `vfs.NewMem` to keep persistence deterministic but still exercise real MANIFEST/table/blob metadata flows across close and reopen. `loadedInfo` is protected by `d.mu` and validates that the event listener fires when initial stats are loaded. The datadriven tests explicitly close snapshots before DB reset, close/reopen the DB, and inspect the current manifest version. The reopen metrics test ensures compression metrics derived from in-memory annotations are reconstructed from persisted table/blob properties after the async collector finishes.

## Dependencies and Integration Points
Dependencies include `datadriven`, `leaktest`, `testify/require`, `manifest`, `keyspan`, `testkeys`, `testutils`, `objstorage`, `objstorageprovider`, `sstable`, `colblk`, and `vfs`. The tests integrate table stats with Pebble DB operations: batching, flushing, ingestion, compaction, manual excision, metrics collection, event listeners, and raw SSTable range-key/range-delete blocks.

## Risks and Edge Cases
The datadriven suite is sensitive to scheduler timing and must explicitly wait on `tableStats.cond` to avoid races. Randomized options in `TestStatsAfterReopen` increase coverage but can make failures need seed/log inspection. Range deletion iterator tests rely on manually constructed `TableMetadata` bounds matching writer metadata; this is valuable for isolating iterator logic, but it does not exercise the whole DB ingestion path. Metrics equality after reopen is a strict signal and may require updates if metric serialization or compression accounting intentionally changes.

## Test Signals
Passing tests signal that stats can be disabled/enabled, pending and initial loads complete, `TableStatsLoaded` is emitted, metadata properties are populated, deletion iterator merging matches expected datadriven output, and compression metrics are stable across reopen. Failures usually point to either async scheduler state, manifest/table property reconstruction, range tombstone span logic, or metric annotation cacheability.
