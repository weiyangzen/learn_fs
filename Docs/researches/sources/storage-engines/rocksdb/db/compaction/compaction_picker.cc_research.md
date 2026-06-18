# sources/storage-engines/rocksdb/db/compaction/compaction_picker.cc

## Purpose
This file implements the compaction picker base-class logic shared by RocksDB compaction styles. It does not contain the full level/universal picker policies, but it provides common machinery for compression selection, intra-L0 cost-based selection, clean-cut expansion, conflict detection against running compactions, manual compact-range and compact-files creation, sanitizing user-specified file sets, registering/unregistering running compactions, and selecting files marked for compaction.

## Important APIs, Types, and Functions
Top-level helpers are `PickCostBasedIntraL0Compaction`, `GetCompressionType`, and `GetCompressionOptions`. `CompactionPicker` methods implemented here include `ReleaseCompactionFiles`, three `GetRange` overloads, `ExpandInputsToCleanCut`, `RangeOverlapWithCompaction`, `FilesRangeOverlapWithCompaction`, `AreFilesInCompaction`, `PickCompactionForCompactFiles`, `GetCompactionInputsFromFileNumbers`, `IsRangeInCompaction`, `SetupOtherInputs`, `GetGrandparents`, `PickCompactionForCompactRange`, `SanitizeCompactionInputFilesForAllLevels`, `SanitizeAndConvertCompactionInputFiles`, `RegisterCompaction`, `UnregisterCompaction`, `PickFilesMarkedForCompaction`, and `GetOverlappingL0Files`.

In debug builds, `AssertCleanCut` verifies that expanded non-L0 inputs do not leave adjacent same-user-key files unselected. The local helper `HaveOverlappingKeyRanges` is used when sanitizing manually specified file numbers against column-family metadata.

## Control Flow
Manual file compaction starts with `SanitizeAndConvertCompactionInputFiles`: it validates output level bounds, ensures inputs are non-empty, expands the input set through `SanitizeCompactionInputFilesForAllLevels`, rejects missing files, files already compacting, and upward compactions, converts file numbers into `CompactionInputFiles`, then rejects overlap with running output compactions. `PickCompactionForCompactFiles` assumes the sanitized set is still protected by the DB mutex, chooses compression, constructs a `Compaction`, and registers it.

Manual range compaction through `PickCompactionForCompactRange` has a special universal all-level path and a normal path. The normal path finds overlapping input-level files, optionally limits non-L0 range size to `max_compaction_bytes`, handles bottommost optimized compaction file-number filtering, expands to a clean cut, computes `compaction_end` for partial progress, sets output level, calls `SetupOtherInputs` to include overlapping output-level files, checks running compaction conflicts, computes grandparents, constructs/registers the `Compaction`, and recomputes compaction score.

Automatic or style-specific pickers use shared helpers. `SetupOtherInputs` includes output-level overlaps, expands them to clean cuts, then opportunistically expands start-level inputs when doing so does not increase output-level inputs and stays under a softened size limit. `PickFilesMarkedForCompaction` tries a random marked file first, then sequentially, skipping files according to a caller predicate and respecting level-0 conflicts. `GetOverlappingL0Files` expands an L0 seed to all overlapping L0 files and checks output-level conflict.

## State and Persistence Behavior
This file does not persist data directly. Its state changes are in-memory scheduling state: `level0_compactions_in_progress_`, `compactions_in_progress_`, `being_compacted` conflict decisions, compaction score recomputation, and `Compaction` objects whose later execution will write version edits. Compression selection persists indirectly by configuring output files. Sanitization uses manifest-derived `ColumnFamilyMetaData` and `VersionStorageInfo` to keep user-selected compactions legal.

## Dependencies and Integration Points
The implementation depends on `VersionStorageInfo`, `Version`, `ColumnFamilyMetaData`, `FileMetaData`, `Compaction`, `MutableCFOptions`, `MutableDBOptions`, `CompactRangeOptions`, `CompactionOptions`, comparators with timestamp-insensitive comparisons, file-name parsing, logging, sync points, and random selection. It is called by DB manual compaction APIs, automatic compaction-style pickers, external SST ingestion conflict checks, and compaction scheduling logic guarded by the DB mutex.

## Risks and Edge Cases
Clean-cut expansion is critical: leaving one version of a user key behind while compacting another can return stale values or reorder merge operands. Running-output overlap checks must include proximal-level outputs when per-key placement is enabled. L0 is special because files overlap and are ordered by recency, so range calculations and conflict rules differ. Manual range compactions can be partial, and incorrect `compaction_end` handling can stall or skip work. Sanitization based on external file numbers must reject missing, compacting, upward, and overlapping files with clear errors.

## Test Signals
Signals come from compact-range, compact-files, level compaction, universal compaction, FIFO, marked-file, ingestion, and per-key-placement tests. `compaction_job_test.cc` covers downstream consequences of grandparent choice and output splitting, while picker-specific tests elsewhere should validate clean cuts, conflict status, manual compaction partial progress, and sanitization errors.
