# sources/storage-engines/pebble/internal/tombspan/tombspan.go

## Purpose
This package tracks "wide" ranged tombstones so Pebble can schedule delete-only compactions that reclaim disk space faster than ordinary compactions. It handles both point-key range deletions and range-key deletions while respecting snapshot isolation.

## Important APIs, Types, and Functions
`WideTombstone` summarizes one or more tombstones with point and range sequence-number ranges, user-key bounds, originating level, and source table. `HighestSeqNum` and `String` expose summary data. `Make(comparer)` initializes a `Set` with a region tree keyed by user-key spans. `Set` stores pending tombstones awaiting snapshot safety and active `tombstonedSpans`. `tombstoneSeqNums.BoundsSeqNums` decides whether a table's point/range contents are older than applicable tombstones using `LargestSeqNumAbsolute`. `AddTombstones` appends and sorts pending tombstones. `UpdateWithEarliestSnapshot` promotes safe pending tombstones into the region tree. `PickCompaction` searches a manifest version for one eligible delete or excise compaction. `DeleteOnlyCompaction` describes the chosen table, level, bounds, and excise/delete mode. `canDeleteOrExciseTable` classifies bounds relationships.

## Control Flow and State
New tombstones enter `pending` sorted by highest sequence number. When the earliest snapshot advances beyond a tombstone's highest sequence number, `UpdateWithEarliestSnapshot` inserts its bounds into the region tree using the low sequence numbers, merging overlapping spans by keeping the maximum point and range tombstone sequence numbers. `PickCompaction` scans region spans, searches lower LSM levels from bottom to top, filters tables whose key kinds and absolute sequence numbers are covered, skips compacting tables while preserving the span, and returns the first complete delete or allowed excise candidate. Spans with no useful future candidates are cleared after iteration. The entire `Set` is in-memory only and intentionally rebuilt from table stats after restart.

## Dependencies and Integration
The package depends on `axisds/regiontree`, Pebble `base` and `manifest`, and standard formatting/sorting packages. It integrates with the table stats collector, LSM version metadata, compaction picker, and delete-only compaction machinery.

## Risks and Edge Cases
Snapshot gating is critical: promoting too early can violate open snapshots. `LargestSeqNumAbsolute` must be used because ordinary compactions can zero sequence numbers. The set is not concurrency-safe; callers must serialize access. If excise is disabled, structurally excisable-only spans are deliberately forgotten, falling back to ordinary compactions. Region tree updates rely on correct comparer ordering and exclusive end bounds.

## Test Signals
`tombspan_test.go` uses datadriven scenarios for adding tombstones, advancing snapshots, marking tables compacting, and picking compactions. It exercises pending promotion, partial promotion, delete/excise choices, and string output.
