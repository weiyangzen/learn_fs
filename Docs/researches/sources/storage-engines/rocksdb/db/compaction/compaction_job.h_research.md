<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job.h

## Purpose

`compaction_job.h` declares the main `CompactionJob` execution class, the data contracts for compaction service input/output/result serialization, and the `CompactionServiceCompactionJob` wrapper used by remote/read-only compaction workers. The header captures the lifecycle contract, mutex expectations, subcompaction model, stats aggregation model, and private helper boundaries implemented in `compaction_job.cc`.

## Important APIs, Types, and Functions

- `class CompactionJob` is the primary compaction executor. Public methods are `Prepare()`, `Run()`, `Install()`, `io_status()`, and a destructor that expects `CleanupCompaction()` to have released `compact_`.
- `CompactionJob::kCompactionAbortedFalse` is a constant abort flag used by compaction service jobs, which do not support normal DB abort signaling.
- Protected helpers expose core overridable/customizable behavior: `RecordCompactionIOStats()`, `LogCompaction()`, `CleanupCompaction()`, and `ProcessKeyValueCompaction()`.
- `UpdateInternalStatsFromInputFiles()`, `UpdateCompactionJobInputStatsFromInternalStats()`, `UpdateCompactionJobOutputStatsFromInternalStats()`, `VerifyInputRecordCount()`, and `VerifyOutputRecordCount()` define the boundary between internal compaction stats and public `CompactionJobStats`.
- Subcompaction scheduling helpers include `GenSubcompactionBoundaries()`, `GetSubcompactionsLimit()`, `AcquireSubcompactionResources()`, `ShrinkSubcompactionResources()`, and `ReleaseSubcompactionResources()`.
- Run-stage helpers split the large execution into `InitializeCompactionRun()`, `RunSubcompactions()`, `UpdateTimingStats()`, `RemoveEmptyOutputs()`, `CleanupAbortedSubcompactions()`, `SyncOutputDirectories()`, `VerifyOutputFiles()`, `AggregateSubcompactionOutputAndJobStats()`, and `FinalizeCompactionRun()`.
- `SubcompactionKeyBoundaries` owns optional start/end slices plus derived timestamp-stripped bounds, max timestamp storage, internal-key bounds, and user-key bounds.
- `SubcompactionInternalIterators` owns the layered input iterator objects used during processing.
- Process helpers include filter validation, read option initialization, input iterator construction, blob builder creation, compaction iterator creation, output file handler creation, key processing, incremental/final stats updates, status finalization, file cleanup, blob finalization, and subcompaction finalization.
- Output helpers include `OpenCompactionOutputFile()`, `FinishCompactionOutputFile()`, `InstallCompactionResults()`, `GetTableFileName()`, and `GetRateLimiterPriority()`.
- Progress helpers include `MaybeAssignCompactionProgressAndWriter()`, `MaybeResumeSubcompactionProgressOnInputIterator()`, `ReadOutputFilesTableProperties()`, `ReadTablePropertiesDirectly()`, `RestoreCompactionOutputs()`, `ShouldUpdateSubcompactionProgress()`, `UpdateSubcompactionProgress()`, `PersistSubcompactionProgress()`, and `UpdateSubcompactionProgressPerLevel()`.
- `struct CompactionServiceInput` serializes the column family, snapshots, expanded input file list, output level, source DB id, optional subcompaction begin/end boundaries, and options file number.
- `struct CompactionServiceOutputFile` serializes metadata for remote-generated SST outputs, including sequence range, internal-key range, oldest ancestor time, creation time, epoch, checksums, paranoid hash, unique ID, table properties, proximal-output flag, and file temperature.
- `struct CompactionServiceResult` carries remote compaction status, output files, output path, bytes read/written, job-level stats, and internal per-level stats.
- `class CompactionServiceCompactionJob : private CompactionJob` exposes a narrower read-only API: `Prepare()`, `Run()`, `CleanupCompaction()`, `io_status()`, and an override of table-file naming and IO stat recording.

## Control Flow

The header documents the main sequencing and lock discipline:

- `Prepare()` requires the DB mutex and builds subcompaction boundaries plus seqno/time state. It accepts optional known single-subcompaction bounds for remote compaction and optional `CompactionProgress` plus a progress log writer for resume support.
- `Run()` requires the DB mutex not be held. It launches subcompaction workers, waits for completion, verifies generated outputs, and unifies bookkeeping.
- `Install()` requires the DB mutex. It writes compaction input/output changes into the current version and releases compaction files via `Compaction::ReleaseCompactionFiles()`.

Internally, the header divides `Run()` into high-level stages and divides each subcompaction into setup, processing, output finalization, stats finalization, and listener notification. This decomposition is important because compaction jobs combine CPU-heavy iteration, file IO, manifest mutation, listener callbacks, and abort/manual-pause paths with different mutex and error-handling requirements.

## State and Persistence Behavior

`CompactionJob` owns transient execution state through `compact_` and durable-output coordination through `versions_`, directories, file options, table cache, blob callback, and `VersionEdit` installation. Public listener stats are accumulated into `job_stats_`; RocksDB internal metrics are accumulated into `internal_stats_`, which contains separate normal-output and proximal-output stats.

The class stores DB identity (`dbname_`, `db_id_`, `db_session_id_`) for file creation, unique IDs, event records, and blob builders. It stores snapshot state (`earliest_snapshot_`, `job_context_`) to decide what sequence numbers and tombstones are still visible. It stores `full_history_ts_low_` and `trim_ts_` to support timestamp-history preservation/trimming. It stores `preserve_seqno_after_` and `proximal_after_seqno_` to decide sequence-number preservation and per-key output placement.

Persistence-related fields include `output_directory_`, `blob_output_directory_`, `db_directory_`, `compaction_progress_writer_`, `options_file_number_`, and the progress-related helper declarations. The header makes clear that resumable progress is not a general multi-subcompaction contract; it is attached through the single-subcompaction path.

## Dependencies and Integration Points

The header depends on most of the DB compaction stack: blob builders/callbacks, column families, compaction iterator/output state, flush/job contexts, internal stats, log writer, memtables, range deletion aggregation, seqno-time mapping, version edits, write controller/thread, event logging, options, Env/FileSystem abstractions, table cache, and public `CompactionJobStats`.

External integration surfaces are:

- Public event listeners, through `CompactionJobStats`, `SubcompactionJobInfo`, and table file creation notifications.
- Compaction service RPC/storage contracts, through `CompactionServiceInput` and `CompactionServiceResult` serialization.
- File-system and rate-limiter behavior, through `FileOptions`, `Env::Priority`, `Env::IOPriority`, `FSDirectory`, and IO tracer.
- DB scheduling, through background compaction scheduled counters and reserved threads.
- BlobDB, through blob output directory/callback and `CompactionServiceOutputFile` blob-related metadata.

## Risks and Edge Cases

- The class is deliberately non-copyable and non-movable because it owns stateful pointers, references, thread-visible subcompaction state, and cleanup-sensitive resources.
- Many constructor arguments are references or raw pointers that must outlive the job; lifetime ownership is external for DB options, mutexes, directories, stats, event logger, job context, and scheduled counters.
- The mutex contract is not enforced by the type system. Misusing `Prepare()`, `Run()`, or `Install()` under the wrong lock state can deadlock or race with version/file state.
- Progress persistence APIs expose a partial feature: only single-subcompaction resume is supported, and implementation-level restrictions exclude several boundary cases.
- Compaction service result serialization must preserve both job-level and internal per-level stats because job-level stats cannot currently be reconstructed exactly from per-level stats.
- Proximal-level output doubles several data paths: stats, output vectors, table properties, range tombstone filtering, manifest edits, and service metadata all need to keep normal and proximal outputs distinct.

## Test Signals

The header exposes `friend class CompactionJobTestBase`, `TEST_Equals()` methods for service input/result structs in debug builds, and many private helpers that have sync-point coverage in the implementation. The mapped stats test validates the public `CompactionJobStats` contract that this class declares and populates. Remote compaction tests should exercise `CompactionServiceInput`, `CompactionServiceOutputFile`, `CompactionServiceResult`, and `CompactionServiceCompactionJob` serialization and path overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.h -->
