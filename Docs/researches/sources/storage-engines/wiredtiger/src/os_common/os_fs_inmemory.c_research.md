# sources/storage-engines/wiredtiger/src/os_common/os_fs_inmemory.c

## Purpose
Implements WiredTiger's in-memory `WT_FILE_SYSTEM`, storing file contents in process memory rather than the OS filesystem.

## Important APIs, Types, and Functions
The private filesystem type `WT_FILE_SYSTEM_INMEM` embeds `WT_FILE_SYSTEM`, hash buckets, a queue of in-memory handles, and a spinlock. Key methods are directory list/free, exist, remove, rename, size, open, terminate, and per-file close/lock/read/size/sync/write. `__wt_os_inmemory` initializes and installs the filesystem.

## Control Flow
All filesystem operations acquire the in-memory filesystem lock. Open searches by name and either returns the existing file if its refcount is zero or creates a new `WT_FILE_HANDLE_INMEM` with read/write/size/sync methods. Reads copy from the backing buffer if the offset is within size. Writes grow the buffer, copy data at the requested offset, and extend size. Rename updates the stored name and rehashes the handle. Remove refuses busy handles unless forced during terminate.

## State and Persistence Behavior
All file data is volatile in `WT_ITEM` buffers attached to in-memory handles. The filesystem maintains name hashes, queue links, per-handle refcount, and content size. Sync is a no-op because there is no durable backing store.

## Dependencies and Integration Points
This file implements the same `WT_FILE_SYSTEM` ABI used by the common handle layer. It depends on connection hash size, spinlocks, `WT_FILE_HANDLE` method conventions, buffer growth, and allocation helpers. It is selected for in-memory connection configurations.

## Risks and Edge Cases
Only one open handle per file is supported; a second concurrent open returns `EBUSY`. Directory listing filters by a directory string prefix and optional filename prefix, which differs from full POSIX directory semantics. Read past EOF returns `WT_ERROR`. Rename does not check destination existence. Because contents are volatile, crash/restart persistence assumptions do not apply.

## Test Signals
In-memory engine tests should cover create/open/read/write/rename/remove/list/size, busy remove/open failures, teardown with forced handle removal, and running normal metadata/logging code over the in-memory filesystem.
