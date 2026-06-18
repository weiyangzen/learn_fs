<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc -->
# sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc

## Purpose
This file implements behavior for `SubcompactionState`, the per-key-range state object used by each subcompaction. It aggregates output stats, exposes combined normal/proximal outputs, cleans up abandoned files, computes output key bounds, and routes iterator output into the correct output group.

## Important APIs, Types, and Functions
Implemented methods are `AggregateCompactionOutputStats`, `GetOutputs`, `Cleanup`, `SmallestUserKey`, `LargestUserKey`, and `AddToOutput`. The methods operate on the two `CompactionOutputs` members declared in the header: normal output-level files and optional proximal-level files for per-key placement.

## Control Flow
`AggregateCompactionOutputStats` asserts builders are closed, adds normal output stats to `internal_stats.output_level_stats`, and, when proximal outputs exist, marks `has_proximal_level_output` and adds proximal stats. `GetOutputs` returns an `OutputIterator` spanning proximal then normal outputs. `Cleanup` closes/clears output builders, and if either subcompaction or overall compaction failed, releases any output files from table cache as obsolete using the compaction's uncache aggressiveness.

`SmallestUserKey` and `LargestUserKey` compare bounds from normal and proximal outputs when both exist, using the column family's user comparator. `AddToOutput` switches `current_outputs_` based on the caller's `use_proximal_output` decision and delegates to `CompactionOutputs::AddToOutput`.

## State and Persistence Behavior
The file manages in-memory output metadata and cache cleanup, not manifest persistence. Successful outputs are later added to a `VersionEdit`; failed outputs are cleaned up and evicted from table cache so uncommitted files are not served. `io_status.PermitUncheckedError()` intentionally suppresses unchecked-status diagnostics during cleanup; the comment notes `io_status` is not handled like `status`.

## Dependencies and Integration Points
It depends on `subcompaction_state.h`, `rocksdb/sst_partitioner.h`, `TableCache::ReleaseObsolete`, `CompactionOutputs`, `OutputIterator`, `CompactionIterator`, range deletion aggregation, and `InternalStats`. It integrates with local compaction jobs, compaction service jobs, per-key placement, cache eviction, and event/job stats.

## Risks and Edge Cases
Stats can include abandoned output files, as noted by the FIXME. Bound calculations must handle either output group being empty. Cleanup only releases cache entries on status failure; durable file deletion is handled elsewhere by obsolete-file processing. `current_outputs_` must remain valid after moves, which is handled in the move constructor in the header.

## Test Signals
Signals include remote per-key placement tests that check output/proximal stats, subcompaction tests that require multiple outputs, failed compaction tests that ensure uncommitted outputs are not installed, and data correctness tests after proximal and normal outputs are mixed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc -->
