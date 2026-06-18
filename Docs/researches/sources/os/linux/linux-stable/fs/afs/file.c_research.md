# File Research: sources/os/linux/linux-stable/fs/afs/file.c

## Summary
Provides regular file operations and netfs integration for AFS. It handles open/release keys, read dispatch, writeback key caching, mmap callback tracking, file size updates, and the `netfs_request_ops` used by buffered and direct I/O paths.

## Main Responsibilities
- Defines AFS file, inode, address-space, and VM operation tables.
- Requests authentication keys on open and validates vnodes before access.
- Caches writeback keys per vnode for later writeback.
- Dispatches synchronous and asynchronous FS/YFS fetch-data operations.
- Wires AFS into netfs read/write helpers.
- Tracks mmap users so callback breaks can invalidate mapped files.

## Key APIs
- `afs_open()`, `afs_release()`.
- `afs_cache_wb_key()`, `afs_put_wb_key()`.
- `afs_fetch_data_operation`.
- `afs_fetch_data_async_rx()`, `afs_fetch_data_immediate_cancel()`.
- `afs_set_i_size()`.
- `afs_req_ops`.

## Important Behavior
Open attaches an `struct afs_file` containing the selected key to `file->private_data`, validates the vnode, and caches a writeback key for writable opens. Release fsyncs writable files, unuses the fscache cookie with updated auxiliary data, drops key references, and prunes stale writeback keys.

`afs_issue_read()` allocates an operation and either executes synchronously or sets `AFS_OPERATION_ASYNC` for readahead/iocb reads. Async receive processing drains rxrpc attention, reports progress to netfs, retries server selection on failure, and terminates the netfs subrequest when done.

`afs_init_request()` attaches a key to read requests, sets read/write sizing, and enables the write stream for regular-file write origins. Request cleanup drops both the request key and writeback key.

## State and Synchronization
`afs_set_i_size()` updates inode size and block count under `vnode->cb_lock` and `inode->i_lock` to avoid tearing and callback races. Mmap users are counted in `cb_nr_mmap` and linked into `volume->open_mmaps` under `open_mmaps_lock`.

## Risks
Read retry and async call lifetime are subtle: `call->op`, `op->call`, rxrpc refs, and netfs subrequest completion must be balanced exactly. Mmap callback tracking has a special zero-count path protected by callback locking and work flushing.
