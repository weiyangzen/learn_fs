# sources/storage-engines/pebble/disk_usage.go

## Purpose
`disk_usage.go` implements disk usage estimation for a user-key range and table/blob metadata annotators that aggregate usage by storage placement. It supports both simple total estimates and estimates split into local, remote/shared, and external-backed storage.

## Important APIs, types, and functions
`(*DB).EstimateDiskUsage(start, end)` returns a total byte estimate for SSTable data overlapping the inclusive range `[start, end]`, delegating to `EstimateDiskUsageByBackingType`. `(*DB).EstimateDiskUsageByBackingType` returns total bytes, remote bytes, external bytes, and an error. It checks closed state, validates inclusive bounds, references the current read state, and obtains a version range annotation from `d.tableDiskUsageAnnotator`.

`TableUsageByPlacement` wraps `metrics.ByPlacement[TableDiskUsage]` and can accumulate local, shared, and external usage. `TableDiskUsage` tracks physical table count/bytes, virtual table count/estimated bytes, and referenced blob bytes. `TotalBytes` sums all byte fields, and `Accumulate` merges another usage value.

`singleTableDiskUsage` builds a placement-keyed usage value for one table using `objstorage.Placement`. `makeTableDiskSpaceUsageAnnotator` creates a `manifest.TableAnnotator` that computes full-table and partial-overlap usage, including estimated referenced blob bytes. `makeBlobFileDiskSpaceUsageAnnotator` creates a blob-file annotator that accumulates physical blob file sizes by placement.

## Control flow, state, and persistence
Usage estimation is read-only. It obtains a referenced `readState` so concurrent compactions cannot delete the underlying version while annotations are computed. Fully contained tables contribute full table size plus estimated referenced blob size. Partially overlapping tables call `d.fileCache.estimateSize` for the overlapping table bytes, then scale the table's estimated referenced blob size by the overlap fraction. Virtual tables are counted separately from physical tables but included in byte totals. `EstimateDiskUsageByBackingType` treats external bytes as part of remote bytes, and remote bytes as part of total bytes.

The annotators are intended to be cached by manifest annotation indexes. The table annotator returns cacheable values for full-table metadata and computes best-effort values for partial overlaps. The blob annotator computes live blob-file usage independently from table-referenced blob bytes.

## Dependencies and integration points
This code depends on `internal/base` for user-key bounds and file types, `internal/manifest` for table and blob annotation infrastructure, `metrics` for count/size and placement aggregation, `objstorage` for placement classification, and `fileCache.estimateSize` for partial SSTable overlap estimates. The resulting annotators are used by `DB.Metrics` in `db.go` and by range-level estimation APIs.

## Risks and invariants
The API excludes WAL bytes for unflushed keys, so callers must treat estimates as SSTable/blob-oriented rather than full end-to-end storage accounting. Partial overlap estimation may overcount blocks when block boundaries or abbreviated index keys prevent exact overlap detection. If `fileCache.estimateSize` returns an error inside the partial-overlap annotator, the code returns an empty usage value, which can undercount silently. Blob referenced bytes are scaled by table overlap fraction, an approximation that may diverge from actual value distribution. The range is inclusive, unlike many Pebble APIs that use end-exclusive bounds, so callers must pass the intended end key carefully.

## Test signals
`disk_usage_test.go` verifies closed-DB panics and uses datadriven tests for open/close, batches, flushes, built tables, ingests, remote builds, external ingests, compactions, total estimates, and backing-type estimates. It asserts `external <= remote <= total`.
