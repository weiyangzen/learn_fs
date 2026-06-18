# sources/storage-engines/rocksdb/db/job_context.h

## Purpose

`job_context.h` defines small containers used by RocksDB background and foreground DB jobs to move slow cleanup, deletion, snapshot release, SuperVersion destruction, WAL writer destruction, and listener notifications out from under the DB mutex. It is a lifetime-management and deferred-work contract, not a persistence format.

`SuperVersionContext` groups pending SuperVersion frees and write-stall notifications. `JobContext` groups obsolete file candidates, live-file snapshots, deletion queues, memtables/WAL writers to free, manifest/log number snapshots, direct-write blob-file protection state, and snapshot context used by flush/compaction jobs.

## Important APIs, types, and functions

- `SuperVersionContext::WriteStallNotification` stores `WriteStallInfo` plus the `ImmutableOptions` whose listeners should be notified.
- `SuperVersionContext::superversions_to_free`, `write_stall_notifications`, and `new_superversion` carry deferred SuperVersion work.
- `SuperVersionContext::NewSuperVersion()`, `HaveSomethingToDelete()`, `PushWriteStallNotification()`, and `Clean()` are the main operations.
- `JobContext::HaveSomethingToDelete()` checks file-deletion queues.
- `JobContext::HaveSomethingToClean()` checks memtables, WAL writers, job snapshot, and nested SuperVersion contexts.
- `GetJobSnapshotSequence()`, `GetLatestSnapshotSequence()`, and `GetEarliestSnapshotSequence()` expose the snapshot boundaries used by jobs.
- `InitSnapshotContext()` initializes snapshot checker, managed snapshot, earliest write-conflict snapshot, and ordered snapshot sequence list once.
- `CandidateFileInfo` represents a filesystem candidate discovered during a full obsolete-file scan.
- Deletion state includes `full_scan_candidate_files`, `sst_live`, `sst_delete_files`, `blob_live`, `blob_delete_files`, `log_delete_files`, `log_recycle_files`, `manifest_delete_files`, and `files_to_quarantine`.
- Direct-write blob protection state includes `active_blob_direct_write_files` and `min_blob_file_number_to_keep`.
- `JobContext::Clean()` performs deferred deletion of SuperVersions, memtables, WAL writers, and managed snapshot release.

## Control flow

DB code constructs a `JobContext` with a job id and optional preallocated SuperVersion. While the DB mutex is held, code populates the context with file numbers and names to preserve or delete, memtables and WAL writers to free, superversions to release, notifications to deliver, and snapshot state needed by a job. Once mutex-protected state has been updated, callers release the DB mutex and invoke `Clean()` or use the deletion queues in purge logic.

`SuperVersionContext::Clean()` first emits write-stall listener callbacks when notifications are enabled, then deletes old `SuperVersion` objects and clears vectors. `JobContext::Clean()` delegates to all SuperVersion contexts, deletes pending read-only memtables and log writers, clears those containers, and resets `job_snapshot`.

Snapshot helper methods require `snapshot_context_initialized` except for `GetJobSnapshotSequence()`, which returns `kMaxSequenceNumber` when no managed snapshot exists. `InitSnapshotContext()` is idempotent: after initialization, later calls return without changing existing context.

## State and persistence behavior

The context stores transient snapshots of persistent state, such as manifest file numbers, log numbers, live SST/blob file numbers, and candidate obsolete file names. It does not itself commit, delete, or persist files. Deletion and purge code consumes the vectors later.

`files_to_quarantine` captures file numbers whose MANIFEST or CURRENT persistence status is ambiguous, preventing premature deletion of newly generated SST/blob files or certain manifest transitions. WAL logs are excluded from this quarantine because minimum WAL retention is updated after successful manifest commits.

The managed snapshot in `job_snapshot` temporarily preserves a sequence boundary for compaction/flush work and is released during `Clean()`.

## Dependencies and integration points

The header depends on column-family definitions, log writer, version set metadata, `autovector`, hash containers, `ManagedSnapshot`, `SnapshotChecker`, `ReadOnlyMemTable`, `SuperVersion`, obsolete file info types, and event listener/write-stall types.

It integrates with `DBImpl::FindObsoleteFiles`, `PurgeObsoleteFiles`, flush jobs, compaction jobs, SuperVersion installation, write-stall notification delivery, WAL recycling/deletion, remote compaction OPTIONS retention, and transaction snapshot conflict logic.

## Risks and edge cases

- Destructors assert cleanup has already happened. Callers must invoke `Clean()` at least once for non-empty contexts and must do it after releasing the DB mutex.
- Listener callbacks in `SuperVersionContext::Clean()` run outside the mutex but can execute arbitrary user code; the context must already contain all information needed for safe notification.
- `InitSnapshotContext()` silently ignores repeated calls, so callers must ensure the first initialization is authoritative.
- `GetLatestSnapshotSequence()` and `GetEarliestSnapshotSequence()` assert initialization; using them before `InitSnapshotContext()` is a debug failure and may hide release-build misuse.
- `min_blob_file_number_to_keep` and `active_blob_direct_write_files` prevent races with direct-write blob files. Incorrect population can either leak obsolete blobs or delete active blobs too early.
- Move construction is supported for `SuperVersionContext`; copying is disabled to avoid double deletion.

## Test signals

Useful coverage includes tests for obsolete file purging, WAL recycling, direct-write blob retention, failed flush/compaction cleanup, SuperVersion install and deferred deletion, write-stall notification order, and snapshot-boundary behavior in compaction. Listener tests that assert write-stall, shutdown, flush, compaction, and background error callbacks also exercise the cleanup/notification design indirectly.
