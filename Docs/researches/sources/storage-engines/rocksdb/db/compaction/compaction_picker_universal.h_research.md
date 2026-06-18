<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h

## Purpose
This header declares the universal compaction picker class. It is the public picker interface used by RocksDB column families configured with `kCompactionStyleUniversal`, while the implementation file contains the detailed run-selection algorithms.

## Important APIs, Types, and Functions
`UniversalCompactionPicker` derives from `CompactionPicker`. Its constructor forwards immutable options and the internal comparator to the base class. `PickCompaction` overrides the base picker and accepts column-family name, mutable CF and DB options, existing snapshots, optional `SnapshotChecker`, mutable `VersionStorageInfo`, a log buffer, `full_history_ts_low`, and an optional `require_max_output_level` flag. `MaxOutputLevel` returns `NumberLevels() - 1`. `NeedsCompaction` reports whether the current version has any universal compaction trigger.

## Control Flow
Callers ask `NeedsCompaction` as a cheap scheduling predicate, then call `PickCompaction` to get a heap-allocated `Compaction` or null. The `require_max_output_level` flag is a caller-side constraint: when true, the implementation only returns a compaction whose output level satisfies the max-output-level requirement.

## State and Persistence Behavior
The class itself stores no additional state beyond the `CompactionPicker` base. It relies on the mutable `VersionStorageInfo` passed to `PickCompaction` for current LSM state and selected-file marking. Persistent effects are indirect through the returned `Compaction` and subsequent version edits committed by the compaction job.

## Dependencies and Integration Points
The header includes `db/compaction/compaction_picker.h` and `db/snapshot_checker.h`, and references `ImmutableOptions`, `InternalKeyComparator`, `MutableCFOptions`, `MutableDBOptions`, `VersionStorageInfo`, `LogBuffer`, `SequenceNumber`, and `SnapshotChecker`. It integrates with the general compaction scheduling framework through virtual methods on `CompactionPicker`.

## Risks and Edge Cases
The header-level contract matters because callers own the returned `Compaction*` and because `require_max_output_level` can intentionally suppress otherwise valid universal compactions. Any signature changes affect compaction scheduling, DB open/manual compaction paths, and tests that instantiate pickers directly.

## Test Signals
Signals are indirect through tests of universal compaction picking and DB-level compaction behavior. Compile-time coverage ensures the picker remains substitutable for `CompactionPicker`; runtime coverage should verify null/non-null selection, max output level behavior, and `NeedsCompaction` scheduling triggers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h -->
