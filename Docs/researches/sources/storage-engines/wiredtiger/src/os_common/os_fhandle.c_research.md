# sources/storage-engines/wiredtiger/src/os_common/os_fhandle.c

## Purpose
Manages common `WT_FH` file-handle lifecycle, shared handle lookup, reference counts, open/close behavior, background fsync, and file zeroing above the configured `WT_FILE_SYSTEM`.

## Important APIs, Types, and Functions
Important functions are `__wt_open`, `__wt_close`, `__wt_handle_is_open`, `__wt_remove_locked`, `__wt_fsync_background_chk`, `__wt_fsync_background`, `__wt_close_connection_close`, and `__wt_file_zero`. Private helpers finalize required `WT_FILE_HANDLE` methods, hash/search handles, open with a specific filesystem, close final handles, and issue one background fsync.

## Control Flow
Open first checks the connection handle hash; if a name is already open it increments the refcount and returns it. Otherwise it allocates a `WT_FH`, applies read-only connection rules, builds a path unless `WT_FS_OPEN_FIXED` is set, calls `fs_open_file`, validates required methods, and inserts the handle after a second race check. Close decrements the refcount under `fh_lock` and only calls the underlying close when it reaches zero. Background fsync walks data handles, temporarily increments references around unlocked fsync calls, and may close handles whose count drops to zero.

## State and Persistence Behavior
Connection state includes hash buckets, a file-handle queue, `open_file_count`, per-handle reference counts, file type, name hash, `written`, and `last_sync`. Persistent effects are underlying file opens, closes, fsyncs, removals through `__wt_remove_locked`, and zero writes through `__wt_file_zero`.

## Dependencies and Integration Points
The file integrates `WT_FILE_SYSTEM` implementations, file operation verbosity, path construction, read-only connection semantics, tiered/local object cleanup, capacity throttling, stats, and background fsync workers.

## Risks and Edge Cases
Method finalization requires close, lock, read, size, sync, and write depending on read-only status; incomplete custom filesystems fail open. Race handling opens a file before the second hash check, so losing the race must close and free the duplicate. Background fsync drops and reacquires `fh_lock`, so reference management is delicate. `__wt_file_zero` uses offset/size arithmetic and throttled writes; callers must pass the intended end range correctly.

## Test Signals
Custom filesystem tests, shared open/close refcount tests, read-only open behavior, background fsync support and no-wait paths, local object remove-while-open behavior, and file-zeroing tests validate this layer.
