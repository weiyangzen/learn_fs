# sources/storage-engines/rocksdb/db/compaction/compaction_picker.h

## Purpose
This header defines the abstract `CompactionPicker` interface and common picker helpers for RocksDB's LSM compaction scheduling. It is the contract implemented by concrete compaction styles and used by DB scheduling/manual compaction code to ask whether compaction is needed, pick automatic compactions, pick manual range/file compactions, track running compactions, and validate user-selected input files.

## Important APIs, Types, and Functions
The primary abstract methods are `PickCompaction` and `NeedsCompaction`; `PickCompactionForCompactRange` is virtual with a shared default implementation. `MaxOutputLevel` defaults to the last configured level. Non-virtual APIs include `SanitizeAndConvertCompactionInputFiles`, `ReleaseCompactionFiles`, `AreFilesInCompaction`, `PickCompactionForCompactFiles`, `GetCompactionInputsFromFileNumbers`, `IsLevel0CompactionInProgress`, `IsCompactionInProgress`, `RangeOverlapWithCompaction`, three `GetRange` overloads, `ExpandInputsToCleanCut`, `IsRangeInCompaction`, `FilesRangeOverlapWithCompaction`, `SetupOtherInputs`, `GetGrandparents`, `PickFilesMarkedForCompaction`, `GetOverlappingL0Files`, `RegisterCompaction`, and `UnregisterCompaction`.

`NullCompactionPicker` is a concrete no-op picker that always returns no compaction and `NeedsCompaction == false`. Free functions `PickCostBasedIntraL0Compaction`, `GetCompressionType`, and `GetCompressionOptions` expose shared policy helpers.

## Control Flow
Concrete style pickers call protected/common helpers to build legal `Compaction` instances. A typical style-specific flow chooses start-level files, calls `ExpandInputsToCleanCut`, calls `SetupOtherInputs`, optionally gathers grandparents, constructs a `Compaction`, and registers it. Manual compaction flows use `SanitizeAndConvertCompactionInputFiles` followed by `PickCompactionForCompactFiles`, or call `PickCompactionForCompactRange` directly.

The running compaction sets are part of the picker contract. Any created compaction should be registered so future picks avoid overlapping output ranges and avoid concurrent L0 compactions where unsupported. `ReleaseCompactionFiles` unregisters and resets next-compaction index on failure.

## State and Persistence Behavior
The header's state is transient scheduler state, not durable storage. `level0_compactions_in_progress_` and `compactions_in_progress_` are protected by the DB mutex. Durable effects occur only after returned `Compaction` objects are executed by compaction jobs and installed into the manifest. The picker does, however, decide output level, compression settings, output path, target file size, max compaction bytes, and input file sets, which shape persistent SST layout.

## Dependencies and Integration Points
The interface depends on `Compaction`, `VersionStorageInfo`, `Version`, `CompactionInputFiles`, `SnapshotChecker`, `LogBuffer`, `CompactRangeOptions`, `CompactionOptions`, `MutableCFOptions`, `MutableDBOptions`, `ImmutableOptions`, and RocksDB `Status`. It is consumed by DBImpl scheduling paths, manual `CompactRange` and `CompactFiles`, concrete level/universal/FIFO pickers, and tests that inspect running compaction state.

## Risks and Edge Cases
API users must hold the DB mutex for methods that inspect or mutate running compaction state. Clean-cut requirements are easy to violate when adding new picker styles. `FilesRangeOverlapWithCompaction` requires both output and proximal level awareness for per-key placement. `PickCompactionForCompactFiles` assumes no mutex release between sanitization and compaction creation; violating that assumption can race with other compactions. `NullCompactionPicker` is useful for disabled compactions but can hide required manual behavior if used accidentally.

## Test Signals
Expected coverage includes style-specific picker tests, DB manual compaction tests, compact-files input validation tests, and conflict tests for concurrent compactions. Public signals are returned `Status` messages from sanitization, absence/presence of picked `Compaction`, and correct registration/unregistration of running work.
