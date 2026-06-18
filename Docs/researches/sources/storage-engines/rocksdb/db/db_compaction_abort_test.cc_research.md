# sources/storage-engines/rocksdb/db/db_compaction_abort_test.cc

## Purpose
`db_compaction_abort_test.cc` is a regression and behavior test suite for RocksDB's compaction abort/resume machinery. It validates that `DBImpl::AbortAllCompactions()` can interrupt manual, automatic, `CompactRange`, `CompactFiles`, subcompacted, bottommost, and style-specific compactions, that `ResumeAllCompactions()` restores progress, and that aborted jobs do not leave visible data loss or orphan SST/blob files.

The suite is also a concurrency test harness. It uses RocksDB sync points to trigger aborts at deterministic internal compaction stages without deadlocking the compaction thread, then checks status codes, statistics, file counts, metadata/disk consistency, and post-resume correctness.

## Important APIs, Types, And Functions
`AbortSynchronizer` is the central helper. It owns an abort thread, atomic `abort_triggered_`/`abort_completed_` guards, and a `port::CondVar`. `TriggerAbort(DBImpl*)` calls `AbortAllCompactions()` on a separate thread so a sync-point callback running on the compaction thread does not block the code path that must observe the abort flag. `WaitForAbortCompletion()` and `Reset()` make repeated abort cycles deterministic.

`SyncPointAbortHelper` wraps `AbortSynchronizer` with `SyncPoint` dependencies. Its `Setup()` installs a dependency from `DBImpl::AbortAllCompactions:FlagSet` to an internal wait point and a callback on a named compaction sync point. This ensures the abort flag is actually set before the compaction code continues past the trigger point. `CleanupAndWait()` disables callbacks and waits for the abort thread.

`DBCompactionAbortTest` extends `DBTestBase` and provides `expected_values_`, optional `Statistics`, `GetOptionsWithStats()`, `PopulateData()`, `VerifyDataIntegrity()`, and `RunSyncPointAbortTest()`. `RunSyncPointAbortTest()` captures `COMPACTION_ABORTED` and `COMPACT_WRITE_BYTES`, expects `CompactRange()` to return `Incomplete` with `IsCompactionAborted()`, resumes, reruns compaction successfully, and checks stats when enabled.

Parameterized fixtures cover varying `max_subcompactions` and compaction styles. The tests directly use public and internal APIs including `CompactRange`, `CompactFiles`, `AbortAllCompactions`, `ResumeAllCompactions`, `TEST_WaitForCompact`, `GetColumnFamilyMetaData`, `IngestExternalFiles`, `SstFileWriter`, blob options, `Env::GetChildren`, and `DestroyDir`.

## Control Flow
The common flow is: configure options to create compactable L0 input, populate multiple flushed files, install a sync-point abort trigger, start compaction, assert an aborted/incomplete status, clean up sync points, wait for the abort API to finish, call `ResumeAllCompactions()`, and rerun or wait for compaction to succeed. Data integrity is verified by reading the latest expected value for each key.

The parameterized subcompaction test runs this flow with `max_subcompactions` set to 1, 2, and 4. The style test runs equivalent abort coverage under level, universal, and FIFO compaction, with FIFO configured for normal intra-L0 compaction rather than file deletion.

Individual tests broaden the timing and API surface. `AbortManualCompaction` uses exclusive manual compaction and triggers during key-value processing. `AbortAutomaticCompaction` aborts a background job triggered by flushes, waits for compaction threads, resumes, and validates later automatic compaction. `AbortScheduledAutomaticCompactionBeforePick` aborts at `BackgroundCallCompaction:0`, before a worker removes queued work, and verifies resume schedules the still-queued compaction.

Cleanup-oriented tests assert no output is installed on abort. `AbortAndVerifyNoOutputFiles` compares L0/L1 counts before and after abort. `AbortWithOutputFilesCleanup` ensures L1 remains empty after an early abort and later receives files after resume. `AbortWithInProgressFileCleanup` enables blob files and forced blob garbage collection, aborts after 100 blob writes, and compares on-disk `.blob`/`.sst` files with column-family metadata to catch orphaned in-progress output files.

Other tests cover repeated and nested control state. `MultipleAbortResumeSequence` runs three abort/resume cycles before a successful compaction. `NestedAbortResumeCalls` calls `AbortAllCompactions()` twice, verifies a single resume is insufficient, and confirms the second resume releases compaction. `AbortBeforeCompactionStarts` sets the abort state before calling `CompactRange()`.

The suite also verifies non-compaction interactions. `AbortDoesNotAffectFlush` confirms memtable flushes still work while compactions are aborted. `AbortCompactFilesAPI` validates abort semantics through `CompactFiles()`. `AbortBottommostLevelCompaction` forces bottommost compaction after creating lower-level data. `AbortThenAtomicRangeReplace` performs `IngestExternalFiles()` with `atomic_replace_range` while compactions remain aborted, then checks replacement/deletion semantics.

## State And Persistence Behavior
The tests treat abort as a durable-state boundary. An aborted compaction must return an aborted status, increment abort stats when configured, avoid installing output files into the manifest, remove or account for any in-progress files on disk, preserve all committed input data, and leave the DB able to compact successfully after `ResumeAllCompactions()`.

`expected_values_` tracks the latest value for overlapping writes so data integrity checks validate logical state across aborted and resumed compactions. File-count assertions inspect level state before and after abort to ensure manifest state did not change as if compaction succeeded. Metadata/disk comparisons in the in-progress cleanup test are stronger: every live `.blob` and `.sst` file left on disk after abort must be represented in column-family metadata, preventing orphan files that are outside normal obsolete-file cleanup.

Nested abort state behaves like a counter or hold count. The suite expects two abort calls to require two resume calls before compactions can proceed. Scheduled automatic compaction state is also persistent in memory: aborting before pick must not lose the queued compaction, and `ResumeAllCompactions()` must re-enable background scheduling.

The atomic range replace test validates that the global compaction-aborted state is scoped to compaction work. External-file ingestion with `atomic_replace_range` installs a replacement version edit while compaction remains aborted; after resume, reads must reflect only the ingested keys and not the replaced range tail.

## Dependencies And Integration Points
This file integrates public RocksDB DB APIs, DBImpl internals, compaction job internals, blob-file writing, external SST ingestion, sync-point instrumentation, and statistics. Required headers include `db/compaction/compaction_job.h`, `db/db_impl/db_impl_secondary.h`, `db/db_test_util.h`, `options/options_helper.h`, `rocksdb/db.h`, `rocksdb/sst_file_writer.h`, and `test_util/sync_point.h`.

Important sync points include `CompactionJob::RunSubcompactions:BeforeStart`, `CompactionJob::ProcessKeyValueCompaction:Start`, `BackgroundCallCompaction:0`, `DBImpl::AbortAllCompactions:FlagSet`, and `BlobFileBuilder::WriteBlobToFile:AddRecord`. The tests depend on compaction code checking the abort flag at those stages and returning a status distinguishable by `IsCompactionAborted()`.

Integration points also include compaction-style options, FIFO-specific settings, `CompactRangeOptions` such as `exclusive_manual_compaction` and `bottommost_level_compaction`, blob garbage collection options, metadata APIs for table/blob files, and external SST writer/ingestion APIs.

## Risks
The largest risk is concurrency. Sync-point callbacks execute on compaction or background threads, while `AbortAllCompactions()` is blocking; calling it inline would deadlock. The helper avoids that but still relies on correct callback cleanup and waiting before resume. Missing `CleanupSyncPoints()` or `WaitForAbortCompletion()` would create cross-test contamination or races.

Abort timing is subtle. Some sync points fire once per subcompaction, so `AbortSynchronizer` guards against spawning multiple abort threads. Tests that assume a particular sync point is reached can become flaky if compaction picking, file sizes, or option defaults change enough that the target path is skipped.

The file-cleanup tests rely on metadata/directory naming conventions for `.sst` and `.blob` files and on file-number parsing from table names. Changes to filename formats, blob metadata exposure, or delayed obsolete-file deletion could require test updates while preserving the same correctness invariant.

`VerifyDataIntegrity()` checks keys present in `expected_values_`, but in tests that write random data without updating `expected_values_` it mostly verifies successful reads. That is intentional for some flows, but stronger value assertions depend on using `PopulateData()`.

## Test Signals
Primary success signals are `Status::IsIncomplete()` plus `IsCompactionAborted()` for aborted compactions, successful compaction after resume, unchanged input file counts immediately after abort where expected, nonzero output files after successful rerun, increased `COMPACTION_ABORTED` and `COMPACT_WRITE_BYTES` tickers, and successful reads of all expected keys.

The highest-value regression signals are absence of orphan SST/blob files after aborting while output files are open, queued automatic compaction still running after resume, nested abort/resume count behavior, flush operations succeeding while compactions are aborted, and atomic range replace correctly replacing the full column family despite the compaction-aborted state.
