# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clbio.c

`nfs_clbio.c` implements FreeBSD NFS client VM/page and buffer-cache I/O: getpages/putpages, buffered reads/writes, direct writes, cache consistency checks, buffer invalidation, async I/O queueing, actual cache-block RPC I/O, and truncate-size handling.

Key functions and behavior:
- `ncl_getpages()` services VM page faults for NFS vnodes. It can delegate to `vfs_bio_getpages()` via the `vfs.nfs.use_buf_pager` sysctl, or perform direct `ncl_readrpc()` into mapped physical pages using a pbuf. It rejects non-cacheable direct-I/O vnodes when mmap is disallowed.
- `ncl_putpages()` writes dirty VM pages back through `VOP_WRITE()`, selecting `n_writecred` when present and trimming writes at EOF. It keeps or clears dirty state depending on write success and `nfs_keep_dirty_on_error`.
- `nfs_bioread_check_cons()` enforces approximate NFS cache consistency by comparing cached modification/size state with fresh attributes, invalidating buffers/directories when modified or stale, and forcing attribute refreshes.
- `ncl_bioread()` implements buffered reads for regular files, symlinks, and directories. It performs fsinfo initialization, max-file-size checks, optional direct read for `IO_DIRECT`, readahead when safe, directory cookie recovery on `NFSERR_BAD_COOKIE`, directory EOF tracking, and buffer-to-uio copying.
- `nfs_directio_write()` performs synchronous direct writes in chunks no larger than mount `wsize`, requiring `FILE_SYNC` and deliberately preventing write-verifier updates from hiding verifier changes from buffered writes.
- `ncl_write()` implements buffered file writes. It handles previous async write errors, fsinfo/wsize setup, append semantics, direct append/write optimization, file-size limits, commit-size pressure, buffer allocation/resizing, non-contiguous write policy, dirty range tracking, sync/async/delayed writes, and `IO_UNIT` rollback on failure.
- `nfs_getcacheblk()` wraps `getblk()` with interruptible-mount signal masking and retry behavior, returning locked cache buffers.
- `ncl_vinvalbuf()` flushes and invalidates vnode buffers/pages, coordinates with NFS exclusive vnode access, handles interruptible/forced dismount behavior, performs pNFS layout commit when needed, and clears `NMODIFIED`.
- `ncl_asyncio()` queues buffers to nfsiod worker threads. It avoids async commit overloads and readdirplus deadlocks, creates/wakes workers, limits queue growth, attaches credentials, and returns `EIO` to force synchronous I/O when no worker can service the mount.
- `ncl_doio()` is the central cache-block RPC executor for synchronous and async paths. It dispatches reads to `ncl_readrpc`, `ncl_readlinkrpc`, `ncl_readdirrpc`, or `ncl_readdirplusrpc`; dispatches writes/commits to `ncl_writerpc`/`ncl_commit`; handles unstable-write commit state; preserves recoverable dirty buffers; records unrecoverable write errors on the nfsnode; and completes buffers with `bufdone()`.
- `ncl_meta_setsize()` updates local file size for truncate/extend, truncates buffers past EOF, adjusts a straddling dirty buffer, and updates vnode pager size.

Important integration points:
- Uses mount flags and state from `nfsport.h`/`nfsmount.h`, node state from `nfsnode.h`, RPC operations declared in `nfsclient/nfs.h`, DTrace cache probes, and global stats in `nfsstatsv1`.
- The code carefully coordinates VM object state, buffer cache state, vnode locks, NFS node locks, and mount locks.
- pNFS-specific behavior appears in invalidation/layout commit handling and in mount-state checks.
- Async I/O uses `nfs_clnfsiod.c` worker state and `ncl_iod_mutex`.

Research notes:
- This is the main client data-path file in the group.
- High-risk areas are cache consistency, dirty-buffer error recovery, append/direct-I/O behavior, lock ordering, and interactions between mmap/pageout and NFSv4 close/stateid handling.
