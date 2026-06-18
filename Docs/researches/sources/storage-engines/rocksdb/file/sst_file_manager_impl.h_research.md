<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.h -->
# sources/storage-engines/rocksdb/file/sst_file_manager_impl.h

## Purpose

`sst_file_manager_impl.h` declares `SstFileManagerImpl`, the concrete `SstFileManager` used to track SST/blob disk usage, throttle deletes, enforce maximum allowed RocksDB space usage, reserve compaction headroom, and coordinate recovery after disk-full errors.

## Important APIs, Types, and Functions

- Public file lifecycle hooks: `OnAddFile`, `OnDeleteFile`, `OnMoveFile`, `OnUntrackFile`.
- Space-limit APIs overriding `SstFileManager`: `SetMaxAllowedSpaceUsage`, `GetTotalSize`, `GetTrackedFiles`, `IsMaxAllowedSpaceReached`, and `IsMaxAllowedSpaceReachedIncludingCompactions`.
- Compaction admission APIs: `SetCompactionBufferSize`, `EnoughRoomForCompaction`, `OnCompactionCompletion`, `GetCompactionsReservedSize`.
- Deletion APIs: `GetDeleteRateBytesPerSecond`, `SetDeleteRateBytesPerSecond`, `GetMaxTrashDBRatio`, `SetMaxTrashDBRatio`, `GetTotalTrashSize`, `ScheduleFileDeletion`, `ScheduleUnaccountedFileDeletion`, trash waiting/bucket APIs, and `delete_scheduler()`.
- Error recovery APIs: `ReserveDiskBuffer`, `StartErrorRecovery`, `CancelErrorRecovery`, and `Close`.
- Private helpers `OnAddFileImpl`, `OnDeleteFileImpl`, `ClearError`, and `CheckFreeSpace`.

## Control Flow

The header defines a thread-safe manager with one mutex protecting most accounting and recovery state. Public methods either mutate tracked-file accounting, delegate deletion to `DeleteScheduler`, adjust options, or participate in compaction/error recovery. `Close()` is part of the lifecycle contract and should be called before destruction to stop the background error-recovery thread.

## State and Persistence Behavior

Important state includes `total_files_size_`, `compaction_buffer_size_`, `cur_compactions_reserved_size_`, `tracked_files_`, `max_allowed_space_`, `delete_scheduler_`, recovery-thread closure state, `path_` for free-space probes, `bg_err_`, `reserved_disk_buffer_`, `free_space_trigger_`, the handler queue, and `cur_instance_`. This state is process-local bookkeeping around durable files; persistence of actual SST/blob files remains in the filesystem and DB manifest/version metadata.

## Dependencies and Integration Points

The class depends on `rocksdb/sst_file_manager.h`, `file/delete_scheduler.h`, compaction metadata declarations, `FileSystem`, `SystemClock`, `Logger`, and `ErrorHandler`. It is the internal implementation behind the public `NewSstFileManager` factory and integrates with DBImpl file lifecycle, compaction scheduling, and background error handling.

## Risks and Edge Cases

All public functions are intended to be thread-safe, so new state must join the mutex discipline. Error recovery stores raw `ErrorHandler*` values and must cooperate with DB shutdown. Exposing `delete_scheduler()` gives internal callers direct access to deletion machinery, which can bypass higher-level policy if misused. The class tracks only files reported to it; external filesystem changes or missed callbacks can make accounting approximate.

## Test Signals

Header-level contracts are validated by tests that instantiate `SstFileManager`, exercise file lifecycle hooks, query size maps, set delete rates and trash ratios, gate compactions, and simulate DB error recovery. Thread-safety tests should stress concurrent add/delete/query and close/recovery interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/sst_file_manager_impl.h -->
