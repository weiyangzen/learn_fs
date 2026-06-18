# sources/storage-engines/rocksdb/db/compact_files_test.cc

## Purpose

This GoogleTest file validates the `DB::CompactFiles()` API. It focuses on manual compaction of explicitly named SST files, including conflict handling with background compaction, output-level validation, obsolete input cleanup, compression option selection, compaction job reporting, pending-file capture, and the optimized trivial-move path.

## Important APIs, Types, and Helpers

- `CompactFilesTest` is a minimal fixture holding a per-thread DB path and default environment.
- `FlushedFileCollector` is an `EventListener` that records `FlushJobInfo::file_path` values under a mutex so tests can pass exact SST filenames to `CompactFiles()`.
- `MakeKey(prefix, index)` creates zero-padded test keys for stable range construction in trivial-move tests.
- Tests use `DB::CompactFiles(CompactionOptions, files, output_level, output_path_id, output_file_name, CompactionJobInfo*)`, `GetColumnFamilyMetaData()`, `GetPropertiesOfAllTables()`, `DBImpl::TEST_WaitForBackgroundWork()`, `DBImpl::TEST_WaitForCompact()`, and `SyncPoint`.

## Control Flow and State Behavior

Most tests disable or control background compaction, write data, flush one or more L0 files, collect their paths, and then invoke `CompactFiles()` to move or merge those files to a target level. The observable state is level metadata, deleted input files, compression/table properties, job-info fields, and data readability.

Important cases:

- `L0ConflictsFiles` creates enough L0 files to start background compaction, then uses sync points so a `CompactFiles()` L0 compaction is in progress when the background compaction checks for conflicts. It validates the background job notices the L0 conflict and avoids overlapping work.
- `MultipleLevel` creates files in L0, L3, L4, and L5, then attempts compaction of a mixed file set. Output levels below the highest input level are rejected with `InvalidArgument`; output to L5 succeeds even while another thread flushes new files.
- `ObsoleteFiles` uses `kCompactionStyleNone`, compacts collected L0 files to L1, waits for compaction cleanup, and verifies the old input filenames no longer exist.
- `NotCutOutputOnLevel0` sets a tiny `max_compaction_bytes` and compacts file sets back to L0, validating output cutting is not applied in an unsafe way for L0.
- `CapturingPendingFiles` starts `CompactFiles()` while another flush creates a new file, then reopens the DB to ensure pending-output capture and obsolete-file handling do not lose needed files.
- `CompactionFilterWithGetSv` uses a compaction filter that calls `DB::Get()` to ensure `CompactFiles()` can run filters that acquire super versions safely.
- `SentinelCompressionType` passes `kDisableCompressionOption` and checks that output compression comes from CF compression settings, using table properties to verify the encoded compression name.
- `CompressionWithBlockAlign` validates block-aligned tables reject incompatible explicit compression but accept the sentinel compression option.
- `GetCompactionJobInfo` checks `CompactionJobInfo` fields including base input level, CF id/name, reason, compression, output level, and status.
- `TrivialMoveNonOverlappingFiles` first compacts non-overlapping L0 files to L1, then moves one non-overlapping L1 file to L6 with `allow_trivial_move=true`. A sync-point callback confirms the trivial-move path, and metadata verifies the same file number moved without rewriting.
- `TrivialMoveBlockedByOverlap` creates an existing L6 range and an overlapping L1 file, then verifies `allow_trivial_move=true` falls back to full compaction when overlap exists and that updated values are visible.

## Dependencies and Integration Points

The test integrates public `DB` APIs with `DBImpl` test hooks, `EventListener` flush callbacks, `ColumnFamilyMetaData`, `TablePropertiesCollection`, compression capability helpers (`Zlib_Supported`, `Snappy_Supported`), block-based table options, and `SyncPoint` labels in compaction code. It also exercises `CompactionOptions::allow_trivial_move`, `compression`, and output-level semantics.

## Risks and Edge Cases

- Filename capture depends on listener callbacks being complete; tests call `TEST_WaitForBackgroundWork()` before consuming listener state to avoid races.
- Compression tests are conditional on library support and can skip when zlib or snappy is unavailable.
- Trivial move correctness is sensitive to file-range overlap detection and level numbering. A bad implementation could preserve metadata movement but break snapshot or overlap invariants.
- `CompactFiles()` accepts user-supplied filenames, so stale, pending, or concurrently obsolete files are an important safety boundary.

## Test Signals

This file is a direct test suite. It signals correctness through `Status` checks, metadata level counts, missing obsolete input files, table compression properties, job-info fields, sync-point callbacks, DB reopen success, and final point reads after trivial or non-trivial compactions.
