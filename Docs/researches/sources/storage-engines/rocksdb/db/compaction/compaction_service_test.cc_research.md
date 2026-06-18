<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc

## Purpose
This file is the main DB-level regression suite for RocksDB compaction service behavior. It installs an in-process `CompactionService` implementation that calls `DB::OpenAndCompact`, then validates remote compaction scheduling, result installation, correctness under options/listeners/filters/merge/snapshots, failure handling, local fallback, corrupt output detection, concurrent compactions, and resumable remote compactions.

## Important APIs, Types, and Functions
`MyTestCompactionService` implements `CompactionService::Schedule`, `Wait`, `CancelAwaitingJobs`, and `OnInstallation`. It stores scheduled input blobs by generated job ID, runs `DB::OpenAndCompact`, propagates selected option overrides, supports injected schedule/wait/result statuses, counts compactions, records start/wait `CompactionServiceJobInfo`, and exposes the last deserialized `CompactionServiceResult`.

`CompactionServiceTest` derives from `DBTestBase` and provides `ReopenWithCompactionService`, `GenerateTestData`, `VerifyTestData`, statistics accessors, and optional remote listeners/table-property collectors. Helper test classes include `EventVerifier`, `PartialDeleteCompactionFilter`, `ResumableCompactionService`, `ResumableCompactionServiceTest`, and `ResumableCompactionKeyTypeTest`.

## Control Flow
Most tests reopen a DB with the test compaction service, create overlapping SSTs through `GenerateTestData`, trigger automatic or manual compaction, wait for compaction, and assert both logical data and service/result metadata. `BasicCompactions` validates ordinary remote execution and remote-vs-primary statistics, then injects worker failure and validates result status and unique ID verification after reopen. `ManualCompaction` exercises bounded and unbounded `CompactRange` plus non-default column families. Standalone range tombstone tests compare universal and leveled behavior and ensure whole-file filtering marks input record counts inaccurate.

Failure-oriented tests inject output file I/O errors, malformed remote result strings, schedule failures, wait aborts, corrupt remote output bytes, truncated output files, and verification flag combinations. Fallback tests force `kUseLocal` from schedule or wait and verify local compaction stats and data correctness. Cancellation tests cover remote-side cancellation, primary-side `CancelAllBackgroundWork`, and service `CancelAwaitingJobs`.

Integration tests validate preserved OPTIONS files for remote workers, event listener behavior on the worker, table property collectors, compaction filters, merge operators, snapshots, per-key placement/precluding last level, job info fields, subcompaction count, and concurrent `CompactFiles`. Resumable tests run multi-phase `OpenAndCompact` with `allow_resumption` toggled, forced file cuts, cancellation at specific keys/sequence numbers, and verification across delete, merge, single delete, range delete, file-boundary multi-version keys, wide columns, and timed puts.

## State and Persistence Behavior
The test service stages output under `dbname_/scheduled_job_id`, mirroring real remote output isolation. Primary installation is then validated through DB metadata, checksums, file existence, and data reads. Options-file tests ensure the primary pins the original options file number for remote compaction even when live options change and obsolete-file cleanup runs. Corruption/truncation tests mutate remote SST bytes before primary import to ensure primary-side verification catches bad output without treating the worker compaction itself as failed.

Resumable tests persist partial compaction progress in the output directory across `OpenAndCompact` calls when `allow_resumption` is true, or deliberately remove/recreate the directory for fresh-start phases. They use `REMOTE_COMPACT_RESUMED_BYTES` and file-write histograms to distinguish resumed work from full reprocessing.

## Dependencies and Integration Points
The suite depends on `DBTestBase`, `DB::OpenAndCompact`, `CompactionService`, `CompactionServiceInput/Result`, statistics tickers/histograms, sync points, file utilities, `SstFileWriter`, external ingestion, event listeners, table property collectors, merge operators, custom checksum factories, block-based table options, unique ID verification, and C++ threading. It exercises compaction service paths through normal DB APIs: automatic compaction, `CompactRange`, `CompactFiles`, `WaitForCompact`, external file ingestion, flush, delete range, snapshots, and column families.

## Risks and Edge Cases
The tests intentionally rely on sync points and in-process remote execution, so timing or callback ordering changes can make failures subtle. Some assertions depend on generated LSM shape, file counts, and stats values; tests pin compression or move files manually where needed. The fake service shares process state with the primary, so comments explicitly simulate file-number collisions and remote output directories that would be separate in production. Resumable tests force one key per output file for measurement simplicity, which is useful but not a production workload shape.

## Test Signals
This file is itself the strongest signal for `compaction_service_job.cc`. Passing it indicates remote compaction preserves data, propagates options and callbacks, imports metadata/stats correctly, handles local fallback, rejects corrupt output under configured verification, supports cancellation semantics, and resumes compaction only when requested and possible. The final `main` registers custom objects and installs stack traces before running all GoogleTests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc -->
