# File Research: sources/os/linux/linux/fs/nfs/direct.c

## Role

`direct.c` implements uncached NFS I/O for `O_DIRECT` and NFS swap I/O. It bypasses the page cache for application buffers while preserving NFS semantics around short I/O, unstable writes, commits, pNFS data-server commits, lock contexts, and async completion.

Primary entry points are `nfs_file_direct_read()`, `nfs_file_direct_write()`, `nfs_swap_rw()`, `nfs_init_directcache()`, and `nfs_destroy_directcache()`.

## Direct Request Lifecycle

Each operation uses `struct nfs_direct_req`, allocated from `nfs_direct_cachep` by `nfs_direct_req_alloc()`. The request tracks inode, open context, lock context, I/O start, max byte count, completed count, first error, async `kiocb`, commit info, work item, spinlock, completion, and internal refcounts.

`get_dreq()` and `put_dreq()` count outstanding pageio/commit work. Final completion flows through `nfs_direct_complete()`, which calls `inode_dio_end()`, completes async `kiocb` if present, signals synchronous waiters, and drops the final kref.

## Direct Reads

`nfs_file_direct_read()` validates zero length, allocates a direct request, captures open and lock contexts, starts direct I/O exclusion unless this is swap, and schedules reads through `nfs_direct_read_schedule_iovec()`.

`nfs_direct_read_schedule_iovec()` pins user pages with `iov_iter_get_pages_alloc2()`, creates `nfs_page` requests, adds them to an NFS pageio descriptor, releases page references, and completes pageio. If no bytes were scheduled, it returns the initial error.

Read completion uses `nfs_direct_read_completion()`. It updates byte counts through `nfs_direct_count_bytes()`, handles EOF/error truncation, marks user-backed pages dirty when needed, releases requests, updates delegated atime, and completes the direct request when all sub-I/O finishes.

## Direct Writes And Commit Flow

`nfs_file_direct_write()` applies `generic_write_checks()` except for swap, rejects unsupported append semantics through higher-level flag checks, allocates a direct request, captures contexts, initializes pNFS DS commit info, starts direct write exclusion, schedules writes with `nfs_direct_write_schedule_iovec()`, invalidates overlapping page cache after non-swap direct writes, waits or returns queued async status, advances `ki_pos`, and invalidates fscache state.

`nfs_direct_write_schedule_iovec()` pins pages, creates `nfs_page` requests, and adds them to write pageio with stable mode `FLUSH_STABLE` for swap or `FLUSH_COND_STABLE` for ordinary direct writes. Soft `-EAGAIN` conditions defer remaining requests onto commit lists for rescheduling.

`nfs_direct_write_completion()` updates completed byte counts, grows local i_size when needed, records delegated mtime, and either releases stable writes or marks unstable writes for commit. It sets flags such as `NFS_ODIRECT_DO_COMMIT`, `NFS_ODIRECT_RESCHED_WRITES`, or `NFS_ODIRECT_DONE`.

Unstable writes are committed by `nfs_direct_commit_schedule()` and `nfs_direct_commit_complete()`. Commit verifier mismatch causes writes to be rescheduled; commit errors are fatal and truncate the reported byte count. `nfs_direct_write_schedule_work()` runs on `nfsiod_workqueue` to commit, reschedule writes, or clear failed requests and zap the mapping.

## Error And Short-I/O Semantics

`nfs_direct_handle_truncated()` and `nfs_direct_count_bytes()` maintain `max_count`, `count`, and `error` so the final result follows kernel direct-I/O conventions: return completed bytes when any exist, otherwise return the first error.

`nfs_direct_truncate_request()` trims the final reported byte count to the start of a failed request. Redo paths use `NFS_IOHDR_REDO` and avoid double completion accounting.

## Integration Points

The file depends on NFS pageio, pNFS commit handling, lock contexts, fscache invalidation, and inode direct-I/O exclusion helpers. It exports `nfs_dreq_bytes_left()` for pNFS layout code to determine remaining direct-I/O range.
