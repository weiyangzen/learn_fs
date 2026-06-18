<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc

## Purpose

`db_impl_compaction_flush.cc` implements RocksDB `DBImpl`'s flush, compaction, manual compaction, background scheduling, and related observability paths. It is the operational center that converts in-memory memtables into persistent SST/blob metadata, selects and runs compactions, coordinates manual and automatic work, publishes new `SuperVersion`s, handles write-stall-aware waiting, and routes background errors into `ErrorHandler`.

The file sits above `FlushJob` and `CompactionJob`: it creates those jobs, enforces DB-wide scheduling and mutex contracts, handles WAL/MANIFEST ordering, and cleans obsolete files after jobs finish. It also implements public APIs such as `Flush()`, `CompactRange()`, `CompactFiles()`, `WaitForCompact()`, `EnableAutoCompaction()`, `PauseBackgroundWork()`, `AbortAllCompactions()`, and timestamp-history advancement.

## Important APIs, Types, and Functions

- `FlushMemTableToOutputFile()` is the single-CF flush path. It syncs closed WALs when needed, picks immutable memtables, prepares direct-write blob-file additions, runs `FlushJob`, installs a new `SuperVersion`, notifies listeners, updates `SstFileManagerImpl`, and records background errors.
- `AtomicFlushMemTablesToOutputFiles()` flushes multiple column families as one manifest-visible unit. It runs multiple `FlushJob`s, waits for all involved memtables to become installable in order, fsyncs distinct output directories, calls `InstallMemtableAtomicFlushResults()`, and rolls back memtable flush state on failure.
- `CompactRange()` and `CompactRangeInternal()` implement manual range compaction, including timestamp-aware range augmentation, optional `full_history_ts_low` persistence, pre-compaction flush, universal/FIFO/leveled strategy differences, bottommost compaction, and optional `change_level` refitting.
- `CompactFiles()` and `CompactFilesImpl()` implement explicit-file compaction. They sanitize input files, check conflicts and disk reservation, support manifest-only trivial moves, otherwise run a user-priority `CompactionJob`, and fill caller-visible output names and `CompactionJobInfo`.
- `RunManualCompaction()` owns `ManualCompactionState` queueing, exclusive/manual conflict handling, cancellation, scheduling into LOW or BOTTOM Env pools, and range continuation for partial manual compactions.
- `BackgroundFlush()`, `BackgroundCallFlush()`, `BackgroundCompaction()`, and `BackgroundCallCompaction()` are the Env worker entry points. They pop queues, execute work under the correct mutex/no-mutex phases, retry or sleep on transient failure, find/purge obsolete files, decrement scheduled/running counters, and signal waiters.
- `MaybeScheduleFlushOrCompaction()` is the scheduler. It consumes `unscheduled_flushes_` and `unscheduled_compactions_`, respects pause/error/shutdown/manual-exclusive gates, applies `GetBGJobLimits()`, and schedules `BGWorkFlush`, `BGWorkCompaction`, or bottom-priority compaction callbacks.
- `EnqueuePendingFlush()`, `EnqueuePendingCompaction()`, `PopFirstFromFlushQueue()`, `PickCompactionFromQueue()`, and queue helpers own `ColumnFamilyData` refs and queue flags.
- `NotifyOnFlushBegin()`, `NotifyOnFlushCompleted()`, `NotifyOnCompactionBegin()`, `NotifyOnCompactionPreCommit()`, `NotifyOnCompactionCompleted()`, and `BuildCompactionJobInfo()` populate listener-facing job metadata.
- `PauseBackgroundWork()`, `ContinueBackgroundWork()`, `DisableManualCompaction()`, `EnableManualCompaction()`, `AbortAllCompactions()`, and `ResumeAllCompactions()` coordinate operational gates around background activity.
- `InstallSuperVersionAndScheduleWork()` publishes a new column-family `SuperVersion`, recomputes global thresholds and memory accounting, enqueues follow-up compaction, and reschedules work.
- `WaitUntilFlushWouldNotStallWrites()`, `WaitForFlushMemTables()`, and `WaitForCompact()` implement user-visible waiting semantics around write-stall avoidance, flush completion, background drain, optional shutdown close, and background errors.
- `EnoughRoomForCompaction()` and `RequestCompactionToken()` integrate `SstFileManagerImpl` space accounting and `ConcurrentTaskLimiterImpl` task throttling.

## Control Flow

Manual flush starts in `Flush()` or `Flush(vector)`, then chooses `FlushMemTable()` or `AtomicFlushMemTables()` depending on DB options and `FlushOptions::force_atomic_flush`. The request path optionally waits until the hypothetical new immutable memtable/L0 file would not stall writes, joins write-thread queues, waits for pending writes, switches memtables, marks immutable lists as flush-requested, enqueues `FlushRequest`s, schedules background work, notifies listeners, and optionally waits through `WaitForFlushMemTables()`.

Background flush workers enter `BackgroundCallFlush()`, increment running counters, reserve pending output file number state, and call `BackgroundFlush()`. `BackgroundFlush()` pops one flush request, filters dropped or not-pending CFs, may reschedule a single-CF request to retain user-defined timestamps, builds `BGFlushArg`s and `SuperVersionContext`s, then calls `FlushMemTablesToOutputFiles()`. The actual flush path syncs closed WALs before permitting SST state to become newer than WAL state, picks memtables only after WAL ordering is safe, releases the DB mutex for file IO/listener callbacks, commits manifest edits inside `FlushJob`, and publishes `SuperVersion`s. `BackgroundCallFlush()` then finds obsolete files, purges outside the mutex, decrements counters, reschedules, fires pressure callbacks, and signals `atomic_flush_install_cv_` and `bg_cv_`.

Automatic compaction starts from `EnqueuePendingCompaction()` and `MaybeScheduleFlushOrCompaction()`. `BackgroundCallCompaction()` wraps counters, pending output capture, error sleep, obsolete-file cleanup, task-token release, pressure notification, and signaling. `BackgroundCompaction()` chooses between prepicked manual work, queued automatic work, intended bottom-priority repicks, deletion compaction, FIFO temperature trivial copy, trivial move, bottom-priority forwarding, and full `CompactionJob`. Full compaction runs `Prepare()` under mutex, releases the mutex for `Run()`, reacquires it for pre-commit listener notification and install, then publishes a `SuperVersion` and releases compaction files.

Manual compaction is queue-driven. `RunManualCompaction()` registers a stack-owned `ManualCompactionState`, optionally waits for all other compactions in exclusive mode, repeatedly asks the column family to pick a compaction for the remaining range, schedules it as prepicked work, waits on `bg_cv_`, and updates the range when only part was compacted. Pause/abort/cancel paths mark the state done with `Incomplete` status and may unschedule pending Env tasks.

`CompactRangeInternal()` layers policy above this scheduler. It can persist `full_history_ts_low`, flush overlapping memtables, find the first overlapped level using metadata or within-file iterator checks, run compactions level-by-level, force bottommost compaction when requested, and optionally call `ReFitLevel()` after pausing background work. `CompactFilesImpl()` bypasses picker policy by constructing explicit input compactions and can perform metadata-only trivial moves by writing a `VersionEdit` directly.

## State and Persistence Behavior

The durable state changes are WAL additions in MANIFEST, SST files, blob-file additions/garbage records, file-level moves/deletions in `VersionEdit`, `full_history_ts_low`, compact cursor updates, and new `SuperVersion` publication. Flush paths carefully order closed WAL sync and `ApplyWALToManifest()` before memtable picking when multi-CF or 2PC recovery requires WAL persistence to cover flushed SST contents.

Single-CF flush uses `FlushJob` with `write_manifest=true` and syncs the output directory. Atomic flush creates per-CF `FlushJob`s with deferred manifest writes, fsyncs distinct output directories, and commits the combined result with `InstallMemtableAtomicFlushResults()`. On atomic failure it cancels unexecuted jobs, rolls back executed memtables, evicts uninstalled table-cache entries, and preserves prepared direct-write blob generations for retry when the same immutable memtables still reference sealed blob files.

Compaction persistence flows through `CompactionJob::Install()`, `VersionSet::LogAndApply()`, or direct trivial-move edits. File-number capture through `CaptureCurrentFileNumberInPendingOutputs()` protects in-flight outputs from obsolete-file deletion. `ReleaseFileNumberFromPendingOutputs()` happens after job completion, followed by `FindObsoleteFiles()` and `PurgeObsoleteFiles()`.

`InstallSuperVersionAndScheduleWork()` is the visibility boundary for readers and later scheduling. It installs the new `SuperVersion`, updates `max_total_in_memory_state_`, resets bottommost/range-deletion marking thresholds, enqueues pending compaction for the affected CF, and calls the scheduler.

Queue state is reference counted. Non-atomic flushes set `queued_for_flush()` and hold a CF ref; atomic flushes intentionally bypass this dedup guard and rely on flush-in-progress filtering. Compaction queues set `queued_for_compaction()` and hold a CF ref until popped or deleted. Manual compactions are not heap-owned by the queue; the queue points at caller stack state while `RunManualCompaction()` waits.

Background error handling is central. Flush distinguishes WAL sync errors, MANIFEST write errors, SST write errors after WAL sync, shutdown, CF drop, and recovery flushes. Compaction maps IO status and `versions_->io_status()` into `BackgroundErrorReason::kCompaction` or `kManifestWrite`, and it requeues failed automatic compactions when background work is still allowed.

## Dependencies and Integration Points

This file integrates with RocksDB's major DB subsystems:

- LSM metadata: `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `VersionSet`, `VersionEdit`, `SuperVersion`, `SuperVersionContext`, compaction pickers, and `InstallMemtableAtomicFlushResults()`.
- Flush and compaction execution: `FlushJob`, `Compaction`, `CompactionJob`, `CompactionJobStats`, `CompactionJobInfo`, `CompactionInputFiles`, `ManualCompactionState`, and `PrepickedCompaction`.
- WAL and recovery: `SyncWalImpl()`, `ApplyWALToManifest()`, `logs_with_prep_tracker_`, 2PC checks, recovery flush reasons, `ErrorHandler`, and recovery error state.
- BlobDB/direct-write: `BlobFilePartitionManager`, external blob file additions/garbages, protected sealed blob files, direct-write generation commit, and blob callback plumbing.
- IO and file management: `FileSystem`, `FSDirectory`, `WritableFileWriter`, `CopyFile`, `TableCache::ReleaseObsolete()`, `SstFileManagerImpl`, table/blob file naming, directory fsync options, and file checksum metadata.
- Scheduling: Env HIGH/LOW/BOTTOM thread pools, unschedule callbacks, `ConcurrentTaskLimiterImpl`, write-controller compaction speedup, background pressure snapshots, and condition variables.
- Observability and testing: `EventLogger`, `EventListener` callbacks, `ThreadStatusUtil`, histograms/tickers, log buffers, `IOSTATS`, perf context includes, and many `TEST_SYNC_POINT` hooks.

## Risks and Edge Cases

- Mutex boundaries are delicate. Flush/compaction jobs intentionally unlock around IO and callbacks; memtable picking, manifest install, queue mutation, and `SuperVersion` publication require `mutex_`.
- WAL/SST ordering is correctness-critical. If closed WAL sync or WAL manifest addition is skipped incorrectly, a flushed SST can survive crash without the WAL records needed by other CFs or prepared transactions.
- Atomic flush has many partial-failure states: executed jobs with uninstalled files, unexecuted picked memtables, dropped CFs, pending blob generations, directory fsync errors, and manifest failure all require different rollback or cleanup behavior.
- Manual compaction cancellation is cooperative and overloaded: pause and user cancellation both map to `ManualCompactionPaused`, while abort uses `CompactionAborted`. Exclusive manual compaction plus cancellation has a known limitation because waiting threads are not automatically awakened by a user-set canceled flag.
- Bottom-priority forwarding can hold an intended compaction and later repick under changed LSM state. The intended-compaction release/recompute path must keep compaction scores and file locks consistent.
- `ReFitLevel()` requires background work to be paused by caller; violating that precondition risks moving files across overlapping concurrent compaction outputs.
- Space checks are advisory and race with real disk use. `SstFileManagerImpl` reservation/completion accounting must be paired, and max-space-reached after flush is converted into a background error.
- Listener callbacks run without the DB mutex. Implementations can observe intermediate state and must not assume the same synchronization as internal code.
- `WaitForCompact(close_db=true)` sets `reject_new_background_jobs_` and calls `Close()` while temporarily unlocking; failure restores the flag, but callers must understand it is more than a passive wait.

## Test Signals

This file is heavily instrumented with `TEST_SYNC_POINT` and callback hooks around WAL sync, memtable picking, flush reschedule, atomic flush wait/install, manual compaction schedule/unschedule, compaction pick/run/install, trivial move, bottom-priority forwarding, refit level, abort/resume, and wait loops. Those hooks are direct signals that concurrency, error injection, and race-ordering tests cover this file.

Nearby tests are expected to exercise `db_compaction_test`, `compact_files_test`, flush/atomic-flush tests, FIFO temperature tests, manual pause/abort tests, listener callback tests, direct-write blob tests, and shutdown/wait-for-compact behavior. The debug helpers in `db_impl_debug.cc` also expose most internal counters and wait paths used by those tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc -->
