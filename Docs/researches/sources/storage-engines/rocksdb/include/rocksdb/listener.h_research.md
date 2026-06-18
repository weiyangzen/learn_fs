# Research: sources/storage-engines/rocksdb/include/rocksdb/listener.h

## Purpose

`listener.h` defines RocksDB's public event notification interface. It supplies structured event payloads and `EventListener` callbacks for flushes, compactions, file creation/deletion, blob files, file I/O, write stalls, background errors, recovery, ingestion, DB shutdown, and background job pressure.

## Important APIs, Types, and Functions

Important payload types include `FileCreationBriefInfo`, `TableFileCreationInfo`, `BlobFileCreationInfo`, `CompactionJobInfo`, `SubcompactionJobInfo`, `FlushJobInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `BackgroundErrorRecoveryInfo`, `IOErrorInfo`, and `BackgroundJobPressure`. Enumerations include `CompactionReason`, `FlushReason`, `BackgroundErrorReason`, and `FileOperationType`, with string helpers for compaction and flush reasons. `EventListener` extends `Customizable`, offers `CreateFromString`, `Type`, `Name`, and many virtual no-op callbacks. `ShouldBeNotifiedOnFileIO()` gates file-I/O finish and error callbacks.

## Control Flow

RocksDB invokes listener callbacks from the thread performing the event: background flush threads call flush callbacks, compaction threads call compaction callbacks, file readers/writers call file-I/O callbacks, and user-operation threads can call ingestion or background-error callbacks. Compaction ordering is explicitly modeled: `OnCompactionBegin`, subcompaction callbacks, `OnCompactionPreCommit` after output files are written but before manifest commit releases inputs, then `OnCompactionCompleted` after commit. File creation callbacks have started and completed variants, and completed callbacks can carry failed status.

## State and Persistence Behavior

The header stores no listener state, but payloads snapshot DB state and file metadata at event time. Some payload references and DB pointers are only valid during callback execution and must be copied for later use. Callbacks observe persistent transitions such as new SSTs, blob files, file deletion, manifest commits, write-stall state, and background error state. `OnBackgroundError` can mutate the pending background error, potentially preventing the DB from entering read-only mode.

## Dependencies and Integration Points

The header depends on advanced options, compaction stats, compression types, customization, `IOStatus`, `Status`, table properties, and core RocksDB types. Usage spans DB implementation, flush/compaction jobs, file readers and writers, C API event listener wrappers, Java event listeners, db_bench, db_stress, BlobDB, external SST ingestion, and tests. HISTORY shows the API is heavily maintained, including atomic flush fixes, pre-commit compaction race avoidance, blob callbacks, file-I/O expansion, and DB shutdown notification.

## Risks and Edge Cases

Callbacks must not throw into RocksDB. Blocking writes, manual compactions, or long work from callbacks can deadlock or slow background workers, especially when compaction is needed to resolve write stalls. Compaction callbacks are skipped during DB shutdown for some cases. `OnCompactionCompleted` fires after input files have been released, so listeners tracking in-progress files should use `OnCompactionPreCommit`. File-I/O callbacks require opting in via `ShouldBeNotifiedOnFileIO`. References passed to callbacks have limited lifetime.

## Test Signals

Signals include `db/db_flush_test.cc` listener ordering tests, DB basic table/blob file listener tests, external SST listener tests, Java `EventListenerTest`, C API listener tests, and db_stress `DbStressListener` checks for pre-commit ordering, background pressure, file I/O, and concurrent compaction tracking. Good assertions cover callback counts, ordering, payload status, file numbers, blob metadata, write-stall transitions, background recovery old/new errors, and absence of deadlocks under callback activity.
