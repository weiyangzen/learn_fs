# File Research: sources/os/linux/linux-stable/fs/nfs/direct.c

## Role

`direct.c` implements uncached/direct I/O for the NFS client, including `O_DIRECT` reads and writes, swap-file I/O through NFS, asynchronous completion, direct write COMMIT handling, and retry/reschedule paths for pNFS and unstable writes. It avoids populating the Linux page cache for direct I/O and relies on NFS server semantics for EOF and write durability.

## Main state

The central object is `struct nfs_direct_req`, allocated from the `nfs_direct_cachep` slab. It carries the inode, open context, lock context, optional async iocb, byte accounting, error state, pNFS data-server commit info, MDS commit info, completion, work item, and a spinlock. `io_count` tracks outstanding pageio/commit activity; `kref` tracks object lifetime.

`nfs_init_cinfo_from_dreq()` adapts a direct request into the generic NFS commit infrastructure by filling `struct nfs_commit_info` with MDS and data-server commit lists and direct commit completion ops.

## Direct read flow

`nfs_file_direct_read()` handles zero-length I/O, allocates a direct request, takes NFS open and lock contexts, records async completion state when the kiocb is asynchronous, marks user-backed pages dirty-after-read when needed, starts direct I/O serialization with `nfs_start_io_direct()`, and schedules pageio with `nfs_direct_read_schedule_iovec()`.

`nfs_direct_read_schedule_iovec()` pins batches of user pages with `iov_iter_get_pages_alloc2()`, slices them into `nfs_page` requests bounded by server `rsize`, adds them to an NFS read pageio descriptor, and completes the descriptor. Completion is handled by `nfs_direct_read_completion()`, which counts bytes, updates delegated atime, optionally marks user pages dirty, removes each `nfs_page`, and completes the direct request when the last I/O reference drops.

Read byte accounting is defensive: `nfs_direct_count_bytes()` computes the covered byte range from each header and `nfs_direct_handle_truncated()` clamps the overall request on EOF or header error so later completions cannot extend the visible result past a truncation point.

## Direct write and commit flow

`nfs_file_direct_write()` performs generic write checks except for swap I/O, rejects no-byte writes, allocates and initializes a direct request, initializes pNFS data-server commit info, and schedules writes with stable mode `FLUSH_STABLE` for swap or `FLUSH_COND_STABLE` for normal direct writes. Normal direct writes also invalidate overlapping page-cache folios after the RPCs are scheduled and then invalidate fscache state with `FSCACHE_INVAL_DIO_WRITE`.

`nfs_direct_write_schedule_iovec()` pins user pages in server `wsize` chunks, creates `nfs_page` requests, locks them, and adds them to a write pageio descriptor. If the descriptor reports a soft `-EAGAIN`, remaining requests are deferred into commit/retry lists and the direct request flag becomes `NFS_ODIRECT_RESCHED_WRITES`.

`nfs_direct_write_completion()` accounts successful bytes, adjusts local `i_size` for extending writes, updates delegated mtime, and either releases requests or marks them for commit/reschedule. Unstable writes set `NFS_ODIRECT_DO_COMMIT` and preserve the write verifier in each request.

Commit handling uses `nfs_direct_commit_schedule()`, `nfs_direct_commit_complete()`, and `nfs_direct_resched_write()`. Commit verifier mismatches cause writes to be re-marked for retransmission. Commit errors are fatal and truncate the visible byte count to the failed request boundary.

Final direct write completion is deferred through `nfsiod_workqueue` via `nfs_direct_write_complete()` and `nfs_direct_write_schedule_work()`. That work either schedules COMMIT, reschedules writes, or clears outstanding requests, zaps mapping cache state, and completes the request.

## Retry and pNFS integration

The completion ops set `NFS_IOHDR_ODIRECT` on pageio headers. Write completion can request `.reschedule_io`, which marks the header redo bit and moves its pages back to commit/retry lists. `nfs_direct_write_reschedule()` scans commit lists, rejoins page groups, clears pNFS data-server commit verifiers, and retransmits with stable writes.

The direct path shares pNFS commit data structures with buffered writeback through `pnfs_init_ds_commit_info`, `pnfs_recover_commit_reqs`, `pnfs_release_ds_info`, and generic NFS commit scanning.

## Swap support

`nfs_swap_rw()` maps swap read/write requests onto direct read/write with `swap = true`. Swap writes bypass generic write checks and are forced stable. On success the swap address-space operation returns zero rather than byte count, matching swap I/O expectations.

## Lifecycle and error behavior

Synchronous direct I/O waits in `nfs_direct_wait()` unless the request has an async iocb, in which case completion returns `-EIOCBQUEUED` to the submitter and later invokes `ki_complete`. `nfs_direct_complete()` always calls `inode_dio_end()`, completes async iocbs with either byte count or error, signals the completion object, and drops the final direct-request reference.

Pinned pages are released after request construction because `nfs_page` objects hold the needed page references. If no bytes were successfully scheduled, the schedule helper ends DIO, releases the direct request reference it would otherwise consume, and returns the construction error or `-EIO`.

`nfs_init_directcache()` and `nfs_destroy_directcache()` create and destroy the direct-request slab cache, with callers declared in `internal.h` and used from NFS inode module init/exit.
