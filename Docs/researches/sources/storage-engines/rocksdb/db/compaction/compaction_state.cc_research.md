<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_state.cc

## Purpose
This file implements the small aggregation helpers for `CompactionState`, the job-wide state container shared by local and remote compaction jobs. It computes global output key bounds and rolls subcompaction stats into job-level structures.

## Important APIs, Types, and Functions
Implemented methods are `CompactionState::SmallestUserKey`, `LargestUserKey`, and `AggregateCompactionStats`. Each delegates to ordered `SubcompactionState` entries stored in `sub_compact_states`.

## Control Flow
`SmallestUserKey` scans subcompactions in increasing key-range order and returns the first non-empty subcompaction output bound. `LargestUserKey` scans in reverse order and returns the last non-empty output bound. `AggregateCompactionStats` iterates every subcompaction, calls `AggregateCompactionOutputStats` into `InternalStats::CompactionStatsFull`, and adds each `CompactionJobStats` into the job aggregate.

## State and Persistence Behavior
No state is persisted here. The functions read output metadata already accumulated in each subcompaction and write aggregate in-memory stats used later for event listeners, compaction result serialization, and internal metrics. Empty output returns `Slice{nullptr, 0}` to distinguish no finished output from a real key.

## Dependencies and Integration Points
The file depends on `compaction_state.h` and, through it, `Compaction`, `SubcompactionState`, `InternalStats`, and `CompactionJobStats`. It integrates with `CompactionJob` and `CompactionServiceCompactionJob` after subcompaction execution.

## Risks and Edge Cases
Correctness depends on the invariant that `sub_compact_states` are ordered by increasing key range. If a subcompaction produces no output, the bound scans skip it. Stats aggregation includes whatever each subcompaction reports, so abandoned-output stat caveats from `SubcompactionState` can flow upward.

## Test Signals
Signals are indirect through compaction job tests, event-listener stats checks, compaction service result stats, and any assertions on smallest/largest output key prefixes. Multi-subcompaction tests are particularly relevant because they validate ordered bound aggregation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.cc -->
