# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clbio.c

This file implements the NetBSD new NFS client’s buffer-cache, VM pager, direct I/O, and asynchronous I/O paths. It is the main bridge between vnode/page-cache operations and the NFS RPC layer (`ncl_readrpc()`, `ncl_writerpc()`, `ncl_commit()`, `ncl_readdirrpc()`, `ncl_readdirplusrpc()`, `ncl_readlinkrpc()`).

Key entry points:
- `ncl_getpages()` services VM page faults by mapping requested pages into a pbuf KVA window, issuing an NFS read RPC, and marking only the bytes actually returned as valid.
- `ncl_putpages()` writes dirty VM pages through `ncl_writerpc()`, selecting unstable or filesync write mode based on pager sync flags, and keeps pages dirty on error when configured.
- `ncl_bioread()` handles cached reads for regular files, symlinks, and directories, including consistency checks, readahead, directory EOF tracking, and `NFSERR_BAD_COOKIE` recovery.
- `ncl_write()` is the cached write path for regular files. It handles append/sync flushing, direct-I/O dispatch, file-size extension, buffer dirty range merging, unstable write commit pressure, and `IO_UNIT` rollback.
- `ncl_vinvalbuf()` flushes and invalidates dirty buffers/pages, coordinates interruptible mounts, clears `NMODIFIED`, and issues pNFS layout commits when required.
- `ncl_asyncio()` queues buffers to nfsiod workers, throttles per-mount queue length, starts new nfsiods, and rejects async commit/readdirplus cases that are unsafe.
- `ncl_doio()` performs the actual buffer read/write/commit operation, either synchronously or from nfsiod.
- `ncl_doio_directwrite()` completes queued direct-I/O writes and releases staging allocations.
- `ncl_meta_setsize()` updates local size state during truncation and trims overlapping cached buffers.

Important behavior:
- Cache coherency is approximate and based on `NMODIFIED`, server mtime, size-change flags, and forced attribute refreshes.
- Regular-file reads use `vp->v_bufobj.bo_bsize`; directory reads use `NFS_DIRBLKSIZ`; symlink reads use `NFS_MAXPATHLEN`.
- Directory reads cache logical-offset-to-cookie state elsewhere, but this file handles cookie invalidation/replay when the server reports stale cookies.
- Direct writes with `IO_SYNC` go straight to `ncl_writerpc()` in `NFSWRITE_FILESYNC` mode. Async direct writes copy user data into staging buffers and enqueue a `B_DIRECT` pbuf to nfsiod.
- Unstable writes mark buffers `B_NEEDCOMMIT`; commit-only I/O is attempted before rewriting data.
- Recoverable write errors such as `EINTR`, `EIO`, and `ETIMEDOUT` keep buffers dirty for retry. Non-recoverable errors invalidate buffers, store `np->n_error`, set `NWRITEERR`, and flush the attribute cache.

Concurrency and integration:
- Uses `np->n_mtx` for nfsnode flags, size, and direct-I/O counters.
- Uses `ncl_iod_mutex` for nfsiod queues and worker assignment.
- Requires vnode locks around invalidation and upgrades locks in consistency/invalidation paths.
- Updates VM and buffer-cache state with `vnode_pager_setsize()`, `vm_object_page_clean()`, `vfs_busy_pages()`, `bufdone()`, `bdwrite()`, `bwrite()`, and `vnode_pager_undirty_pages()`.

Research notes:
- This is the central file to inspect for NFS client data-integrity behavior, especially unstable write/commit handling, append races, direct-I/O staging, and mmap/page-cache interactions.
- The most delicate paths are `ncl_write()` dirty-range merging, `ncl_doio()` error classification, and `ncl_asyncio()` queue/worker coordination.
