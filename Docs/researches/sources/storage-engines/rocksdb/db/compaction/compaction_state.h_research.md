<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_state.h

## Purpose
This header defines `CompactionState`, the job-wide holder for a `Compaction`, its subcompaction states, and the aggregate status. It is used by both `CompactionJob` and `CompactionServiceCompactionJob` to keep sub-job outputs and stats under one compaction-level object.

## Important APIs, Types, and Functions
`CompactionState` exposes `Compaction* const compaction`, `std::vector<SubcompactionState> sub_compact_states`, and `Status status`. Its methods are `AggregateCompactionStats`, `SmallestUserKey`, and `LargestUserKey`. The constructor requires a non-owning `Compaction*`.

## Control Flow
The header establishes the ordering contract: subcompaction states must be stored in increasing key-range order. Callers fill `sub_compact_states` during compaction preparation, execute them, and then use the declared aggregation/bound helpers after output files close.

## State and Persistence Behavior
`CompactionState` owns the vector of `SubcompactionState` objects but not the `Compaction` pointer. It carries in-memory execution status and output metadata until the compaction job commits or cleans up. Persistence occurs elsewhere through version edits and output file installation.

## Dependencies and Integration Points
The header includes `compaction.h`, `subcompaction_state.h`, and `internal_stats.h`. It integrates with local compaction jobs, compaction service jobs, event listener construction, stats aggregation, and output metadata installation.

## Risks and Edge Cases
Because `compaction` is a raw non-owning pointer, lifetime must be managed by the owning compaction job. The ordered-subcompaction invariant is not enforced by the type system but is required for key-bound helpers. Any move behavior of subcompaction state must preserve output pointers, which is handled in `SubcompactionState`.

## Test Signals
Coverage comes from successful local/remote compactions, subcompaction tests, compaction-service stats checks, and assertions on output key prefixes. Bugs usually appear as wrong aggregate stats, wrong smallest/largest output keys, or cleanup/install behavior failing after one subcompaction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.h -->
