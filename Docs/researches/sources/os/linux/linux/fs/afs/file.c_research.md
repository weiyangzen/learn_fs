# File Research: sources/os/linux/linux/fs/afs/file.c

## Purpose
Provides VFS file operations, address-space operations, netfs integration, mmap tracking, file open/release handling, and data fetch operation glue for regular AFS files.

## Main Responsibilities
- Registers regular-file operations in `afs_file_operations`, including reads, netfs writes, mmap, splice, fsync, and locking.
- Manages per-open authentication keys and per-vnode writeback key caching.
- Bridges netfs read requests to AFS/YFS `FetchData` operations.
- Tracks mmapped vnodes so callback invalidation can affect active mappings.
- Maintains inode size and cache coherency for fetched and written data.

## Key Functions and Data
- `afs_open()` requests a key, validates the vnode, caches a writeback key for write opens, and uses the fscache cookie.
- `afs_release()` fsyncs write opens, unuses fscache, drops keys, and prunes writeback keys.
- `afs_issue_read()` allocates an `afs_operation`, attaches the vnode and subrequest, and dispatches sync or async fetches.
- `afs_fetch_data_async_rx()` and `afs_read_receive()` process asynchronous RxRPC read progress and retry server rotation.
- `afs_req_ops` supplies netfs callbacks for request init/free, reads, writes, writeback, cache invalidation, and size updates.
- `afs_vm_ops` tracks mmap opens/closes and validates callbacks before `map_pages`.

## Important Details
- Direct I/O reads are routed to `netfs_unbuffered_read_iter()`, while buffered reads validate the vnode then call `filemap_read()`.
- `afs_set_i_size()` updates size under callback and inode locks, avoiding tearing on 32-bit systems and updating fscache metadata.
- Open mmaps are linked through `volume->open_mmaps` when `cb_nr_mmap` transitions from zero.
- Write begin rejects writes to vnodes marked `AFS_VNODE_DELETED`.
