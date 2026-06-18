<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h -->
# sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h

## Purpose
This header defines `SubcompactionState`, the state and output container for one subcompaction key range. It is shared by normal compaction and compaction service jobs and supports both ordinary output-level files and proximal-level outputs for per-key placement.

## Important APIs, Types, and Functions
Public fields include the non-owning `const Compaction* compaction`, optional inclusive `start` and exclusive `end` bounds, `Status status`, `IOStatus io_status`, notification flag, `CompactionJobStats`, and `sub_job_id`. Output methods include `GetOutputs`, mutable output accessors, `Outputs`, `OutputStats`, `Current`, `AddOutputsEdit`, `AddToOutput`, `CloseCompactionFiles`, `RemoveLastEmptyOutput`, `CleanupOutputs`, and `Cleanup`. Range tombstone support is exposed through `AssignRangeDelAggregator`, `RangeDelAgg`, and `HasRangeDel`. Job-event helpers include `BuildSubcompactionJobInfo`, `GetWorkerCPUMicros`, and progress getters/setters.

## Control Flow
Construction initializes normal and proximal `CompactionOutputs` and sets an output split key on normal outputs for round-robin support. Copy is disabled; move construction transfers outputs, aggregator, status, stats, and resets `current_outputs_` to point at the moved-to normal or proximal member. `AddToOutput` chooses the active output group for each compaction iterator key. `CloseCompactionFiles` closes proximal outputs first when per-key placement is enabled, then normal outputs, always attempting close even when current status is non-OK so builders are not leaked.

`AddOutputsEdit` writes proximal outputs to `compaction->GetProximalLevel()` and normal outputs to `compaction->output_level()`. `BuildSubcompactionJobInfo` packages column-family, level, reason, compression, stats, and blob compression information for event listeners.

## State and Persistence Behavior
The class owns `CompactionOutputs` objects that hold builders, output metadata, table properties, validators, and stats until the compaction is installed or cleaned up. It owns a `CompactionRangeDelAggregator` used to route range tombstones to the appropriate output. It does not own the `Compaction` pointer. Persistence happens when output files are closed and later added to `VersionEdit`; cleanup abandons builders and cache entries for failed work.

## Dependencies and Integration Points
The header depends on blob file additions and garbage metering, `Compaction`, `CompactionIterator`, `CompactionOutputs`, `InternalStats`, `OutputValidator`, and `CompactionRangeDelAggregator`. It integrates with compaction job preparation/execution, event listener begin/completion notifications, range deletion handling, per-key placement/preclude-last-level logic, output validation, and compaction service result import/export.

## Risks and Edge Cases
The two-output-group design makes pointer correctness important: `current_outputs_` must always point to a member of the current object, especially after moves. Proximal-output access asserts that the compaction supports per-key placement. Range deletion aggregators are single-assignment. Output closing can open new files while finalizing range deletions, so it must run even after earlier errors. The `start`/`end` optional slices are non-owning views, so their source storage must outlive preparation/use.

## Test Signals
Coverage comes from subcompaction tests, per-key placement tests, compaction service `PrecludeLastLevel`, remote event listener tests, range deletion compaction tests, and failure cleanup tests. Key signals are correct output levels in version edits, accurate normal/proximal stats, valid subcompaction job info, no stale cache use after failed compactions, and correct key bounds from mixed output groups.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h -->
