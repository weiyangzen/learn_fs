<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job.cc

## Purpose

`compaction_job.cc` implements the runtime of a RocksDB compaction job. It turns a selected `Compaction` into one or more `SubcompactionState`s, optionally delegates work to a compaction service, scans input internal keys through `CompactionIterator`, writes table/blob outputs, verifies and installs those outputs into the MANIFEST through `VersionEdit`, and publishes both internal and listener-visible statistics.

The implementation is the bridge between compaction planning (`Compaction`, `VersionSet`, `VersionStorageInfo`) and persistence side effects: SST creation, blob file creation, MANIFEST mutation, directory sync, table cache verification, event listener callbacks, thread status, perf/IO stats, and resumable compaction progress.

## Important APIs, Types, and Functions

- `GetCompactionReasonString()` and `GetCompactionProximalOutputRangeTypeString()` convert enum values into logging/event strings.
- `CompactionJob::CompactionJob()` initializes a `CompactionState`, file options optimized for compaction reads, thread-status metadata, snapshot state, blob/output directories, and job-level stats derived from compaction inputs.
- `Prepare()` must run under DB mutex. It computes write lifetime hints, bottommost state, subcompaction key boundaries, optional progress resume state, seqno-to-time mappings, `preserve_seqno_after_`, `proximal_after_seqno_`, and the active options file number.
- `GenSubcompactionBoundaries()` samples approximate table anchors, sorts/deduplicates user-key anchors, computes target range sizes, and creates split boundaries. Round-robin level compaction can reserve extra background threads beyond `max_subcompactions`.
- `Run()` drives the no-mutex phase: log start, run subcompactions, sync directories, verify outputs, aggregate stats, verify record counts, and finalize job status.
- `ProcessKeyValueCompaction()` is the per-subcompaction body. It handles remote-service fallback, compaction filter validation, listener notifications, input iterator layering, progress resume, merge helper creation, `CompactionIterator` creation, the key loop, cleanup, blob finalization, and stats finalization.
- `ProcessKeyValue()` is the central key loop. It periodically checks `compaction_aborted_`, records incremental stats, decides proximal-vs-last-level placement by sequence number, calls `SubcompactionState::AddToOutput()`, and advances the compaction iterator.
- `OpenCompactionOutputFile()` allocates a new file number, creates a writable SST file, initializes `FileMetaData`, unique IDs, temperature, `WritableFileWriter`, and `TableBuilderOptions`.
- `FinishCompactionOutputFile()` adds range tombstones, finishes the table builder, syncs/closes the writer, removes empty SSTs, emits table creation events, notifies the SST file manager, and persists resumable progress when eligible.
- `InstallCompactionResults()` adds input deletions, output SSTs, blob additions, blob garbage accounting, round-robin compact cursor state, and calls `VersionSet::LogAndApply()` with a callback that releases compaction input files.
- `MaybeResumeSubcompactionProgressOnInputIterator()`, `UpdateSubcompactionProgress()`, and `PersistSubcompactionProgress()` restore and persist single-subcompaction progress records through `VersionEdit::SetSubcompactionProgress()`.
- `UpdateInternalStatsFromInputFiles()`, `UpdateCompactionJobInputStatsFromInternalStats()`, `UpdateCompactionJobOutputStatsFromInternalStats()`, `VerifyInputRecordCount()`, and `VerifyOutputRecordCount()` reconcile table properties, iterator counters, output table properties, and public `CompactionJobStats`.

## Control Flow

The normal lifecycle is `Prepare()` -> `Run()` -> `Install()` -> `CleanupCompaction()`.

During `Prepare()`, the job builds subcompactions either from generated user-key boundaries or from a known single range used by remote compaction/resume flows. Boundary generation releases the DB mutex while reading table anchor estimates, then may reserve additional Env threads for round-robin compaction. `Prepare()` also gathers input table seqno-time metadata when time preservation/tiering is enabled, derives the sequence-number threshold for preserving sequence numbers, and derives `proximal_after_seqno_` for per-key placement into proximal output versus last-level output.

`Run()` executes subcompactions in parallel: subcompaction 0 runs on the caller thread and the rest run on `port::Thread`s. After all threads join, empty output builders are removed and reserved extra subcompaction resources are released. The job then checks subcompaction status, optionally deletes aborted output files, fsyncs output directories, verifies output files by reopening/iterating/checksumming according to `verify_output_flags`, records output table properties on the `Compaction`, aggregates subcompaction stats, builds input stats from table metadata, and verifies input/output record counts when possible.

Inside a local subcompaction, the input iterator stack is `VersionSet::MakeInputIterator()` plus optional `ClippingIterator`, optional `BlobCountingIterator`, and optional `HistoryTrimmingIterator`. `CompactionIterator` applies snapshot/drop/merge/filter/range-deletion rules and emits records to `SubcompactionState::AddToOutput()`. File open/close are callbacks into `OpenCompactionOutputFile()` and `FinishCompactionOutputFile()`, so file rollover is controlled by `CompactionOutputs` while physical file construction remains in `CompactionJob`.

`Install()` returns to the DB mutex. It adds internal stats to the column family, applies the `VersionEdit`, logs human and structured event records, propagates install failure into `compact_->status` so cleanup releases uninstalled table-cache entries, and deletes `CompactionState`.

## State and Persistence Behavior

The persistent outputs are SST files, blob files, MANIFEST edits, directory fsyncs, and optional compaction progress log records. `OpenCompactionOutputFile()` tracks every new output path in `CompactionOutputs` so abort cleanup can delete files even if they were not retained in final output vectors. `FinishCompactionOutputFile()` deletes empty SSTs, records `TableProperties`, preserves file checksums, and integrates with `SstFileManagerImpl` quota enforcement.

`InstallCompactionResults()` is the MANIFEST boundary. It records deleted input files, added output files for normal and proximal levels, blob additions, blob garbage counts, and round-robin compact cursor state. It uses `VersionSet::LogAndApply()` and releases compaction files via callback only after the manifest path has progressed.

Resumable compaction is intentionally narrow: progress is attached only when there is exactly one subcompaction. Progress persistence is skipped for timestamped comparators, range-deletion file boundaries, same-user-key adjacent output files, final output files, empty outputs, and cases where `CompactionIterator` has looked ahead at the current key. On resume, previously completed outputs are restored from recorded `FileMetaData` plus table properties read directly from the output files, and file-number allocation is advanced past restored outputs.

Stateful stats include `internal_stats_`, per-subcompaction `compaction_job_stats`, `job_stats_`, perf counters, `io_status_`, thread-status properties, seqno-to-time mapping, blob garbage meters, and `SubcompactionProgress`.

## Dependencies and Integration Points

This file integrates with:

- LSM/versioning: `Compaction`, `CompactionState`, `SubcompactionState`, `VersionSet`, `VersionEdit`, `ColumnFamilyData`, `VersionStorageInfo`.
- Iteration and compaction semantics: `CompactionIterator`, `MergeHelper`, `CompactionRangeDelAggregator`, `ClippingIterator`, `HistoryTrimmingIterator`, `BlobCountingIterator`.
- File/table IO: `FileSystem`, `FSDirectory`, `WritableFileWriter`, `TableBuilder`, `TableCache`, `TableReader`, table properties, unique SST IDs, file checksums.
- BlobDB: `BlobFileBuilder`, `BlobFileCompletionCallback`, blob additions, blob garbage accounting.
- Observability: `EventLogger`, event listeners, `ThreadStatusUtil`, histograms/tickers, `IOSTATS`, sync points.
- Scheduling: `Env::ReserveThreads()`/`ReleaseThreads()`, background compaction scheduled counters, write-controller-aware IO priority.
- Compaction service: `ShouldUseLocalCompaction()` delegates to service processing when `db_options_.compaction_service` is configured, otherwise falls back locally.

## Risks and Edge Cases

- `CompactionJob` assumes a strict mutex contract: `Prepare()` and `Install()` need DB mutex, while `Run()` must not hold it. Boundary generation deliberately unlocks during table anchor reads.
- Additional subcompaction resources mutate shared scheduled-compaction counters and must be released on all paths. Leaks here can distort background scheduling.
- Abort cleanup deletes tracked output paths only when progress persistence is not active. Resumable compaction keeps files for later restoration, so stale or corrupt progress can leave durable partial outputs until recovery logic handles them.
- Record-count verification is disabled or softened in several cases: old block-based table format versions with unreliable entry counts, timestamp trimming, table factories without output table property support, and configured non-fatal verification.
- Progress persistence relies on user-key boundary safety. Same-user-key boundaries, range tombstones, merge/lookahead behavior, and timestamped keys are deliberately excluded because naive resume would double-count or lose versions/tombstones.
- Per-key/proximal placement splits range tombstones by sequence-number interval and traverses them twice when needed. This is correct but potentially CPU-heavy for tombstone-heavy workloads.
- Output verification may be expensive: iteration checksum and file checksum verification can reread all outputs, including remote compaction outputs when enabled.
- `ReadOutputFilesTableProperties()` accepts an `is_proximal_level` label but the resume call currently passes the default value even for proximal outputs, affecting only diagnostics.

## Test Signals

The file has extensive sync points for unit tests around subcompaction resource reservation, output file opening/finishing, manual pause, abort checks, record-count verification, and progress/tiering thresholds. The mapped `compaction_job_stats_test.cc` validates listener-visible job stats for level and universal compactions, deletion-drop counters, compression-size tolerances, subcompaction-dependent output-file counts, and IO timing stats. Other nearby compaction tests likely exercise abort cleanup, progress resume, proximal-level placement, remote compaction, and output verification because the implementation exposes explicit `TEST_SYNC_POINT` hooks for those paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.cc -->
