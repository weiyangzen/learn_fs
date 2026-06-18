<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc -->
# sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc

## Purpose

`sst_file_manager_impl.cc` implements `SstFileManagerImpl`, RocksDB's concrete manager for tracking SST/blob file disk usage, enforcing configured space limits, throttling file deletion through `DeleteScheduler`, and coordinating no-space error recovery across DB instances. It is a production boundary between DB version/file lifecycle code and filesystem capacity/deletion behavior.

## Important APIs, Types, and Functions

- Constructor/destructor/`Close()` initialize deletion scheduling, counters, mutex/condition variable state, and the background recovery thread lifetime.
- `OnAddFile()`, `OnAddFile(file_size)`, `OnDeleteFile()`, `OnMoveFile()`, and `OnUntrackFile()` maintain `tracked_files_` and `total_files_size_`.
- `SetMaxAllowedSpaceUsage()`, `IsMaxAllowedSpaceReached()`, and `IsMaxAllowedSpaceReachedIncludingCompactions()` enforce configured SST/blob space caps.
- `EnoughRoomForCompaction()` reserves approximate compaction input size as temporary headroom before a compaction starts.
- `OnCompactionCompletion()` releases compaction reservation after completion.
- `ReserveDiskBuffer()`, `StartErrorRecovery()`, `CancelErrorRecovery()`, and `ClearError()` implement no-space recovery polling across `ErrorHandler` instances.
- `ScheduleFileDeletion()`, `ScheduleUnaccountedFileDeletion()`, `WaitForEmptyTrash()`, `NewTrashBucket()`, and `WaitForEmptyTrashBucket()` delegate to `DeleteScheduler`.
- `NewSstFileManager()` overloads create the implementation and optionally schedule deletion of legacy trash-dir files.

## Control Flow

File tracking operations acquire `mu_` and call small internal helpers. `OnAddFile()` optionally queries file size through the filesystem, while the overload trusts a caller-supplied size. `OnMoveFile()` adds the new path with the old tracked size and then removes the old path. Delete and untrack are identical for accounting.

`EnoughRoomForCompaction()` sums all compaction input file sizes, rejects the compaction if tracked size plus existing reservation plus this compaction plus `compaction_buffer_size_` exceeds `max_allowed_space_`, and applies a stricter free-space check after a DB has seen a no-space soft error. In soft-error mode it calls `GetFreeSpace()` on a representative table filename and requires enough headroom for current reservations plus this compaction, and possibly the reserved disk buffer. On success it increments `cur_compactions_reserved_size_` and snapshots `free_space_trigger_`.

Error recovery starts when DB error handling reports a soft or hard no-space error. `StartErrorRecovery()` records the most severe relevant background error, queues the `ErrorHandler`, joins any previous recovery thread, and starts a new `port::Thread` running `ClearError()`. `ClearError()` loops while handlers remain: it checks free space against hard-error reserved buffer or soft-error trigger, invokes `RecoverFromBGError()` outside the mutex for the front handler, removes handlers that recovered, shut down, or escalated to fatal, waits between attempts, and clears `bg_err_` when the queue drains. `CancelErrorRecovery()` removes a handler from the queue or nulls `cur_instance_` if the thread is currently working on it.

## State and Persistence Behavior

The manager maintains in-memory state only: tracked file path-to-size map, total tracked size, configured max allowed space, compaction reserved bytes, deletion scheduler state, reserved disk buffer, free-space trigger, current background error, and queued `ErrorHandler` pointers. The durable effects are filesystem deletes/trash scheduling and DB error recovery attempts. Tracking state is rebuilt by DB instances through lifecycle callbacks; it is not itself persisted.

## Dependencies and Integration Points

This implementation depends on `DeleteScheduler`, `FileSystem`, `SystemClock`, `Logger`, `ErrorHandler`, compaction metadata (`Compaction`, `CompactionInputFiles`, `FileMetaData`), table filename helpers, `Status` severity/subcode semantics, RocksDB mutex/condition variable wrappers, and sync points. DBImpl and column-family code call it when SST/blob files are created, moved, deleted, untracked, or when compaction and no-space recovery decisions are needed.

## Risks and Edge Cases

Accounting correctness depends on all DB file lifecycle paths calling the matching add/delete/move/untrack methods exactly once. `OnMoveFile()` indexes `tracked_files_[old_path]`, which inserts a zero-size entry if the old path was missing before adding the new path; callers must only move tracked files. Compaction reservation is conservative and based on input sizes, so it can reject compactions even when output would be smaller. Soft-error recovery is intentionally per-SFM and can throttle compactions of a DB that has reported no-space while trying not to penalize unrelated DBs. `ClearError()` carefully releases the mutex before DB recovery callbacks, but lifetime safety relies on `ErrorHandler`'s recovery-in-progress coordination and `CancelErrorRecovery()` semantics.

## Test Signals

Signals include tracked size changes on add/delete/move, max-space rejection behavior with and without compaction reservations, reservation release after `OnCompactionCompletion()`, delete scheduler trash size and bucket behavior, no-space soft/hard recovery callbacks, cancellation while a handler is current, legacy trash cleanup during `NewSstFileManager()`, and sync-point-observable file lifecycle callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.cc -->
