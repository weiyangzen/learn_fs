# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vnops.c

## Purpose
Implements NFSv2 vnode operations: open/close, read/write, attribute operations, access checks, lookup/create/remove/rename/link/mkdir/rmdir/symlink/readdir, VM page cache integration, mmap handling, record/share locking, ACL hooks, pathconf, and fid generation.

## Main Entry Points
- `nfs_vnodeops_template[]` registers all VOP callbacks for NFSv2.
- `nfs_open()` and `nfs_close()` enforce close-to-open consistency, credential retention, lock cleanup, page flushing, and delayed write error reporting.
- `nfs_read()` and `nfs_write()` implement VM-cached I/O through segmap/VPM plus direct/no-cache paths using `nfsread()` and `nfswrite()`.
- `nfs_getattr()`, `nfs_setattr()`, and `nfssetattr()` manage cache validation, dirty-page flushing, permission policy, NFS SETATTR RPCs, truncation, time conversion, and ACL/access cache purge.
- `nfs_lookup()`, `nfslookup()`, `nfslookup_dnlc()`, and `nfslookup_otw()` implement directory lookup, extended attribute lookup, DNLC positive/negative caching, and failover-aware LOOKUP RPCs.
- Directory mutation callbacks include `nfs_create()`, `nfs_remove()`, `nfs_link()`, `nfs_rename()`/`nfsrename()`, `nfs_mkdir()`, `nfs_rmdir()`, and `nfs_symlink()`.
- Page and mmap callbacks include `nfs_getpage()`, `nfs_getapage()`, `nfs_readahead()`, `nfs_putpage()`, `nfs_putapage()`, `nfs_sync_putapage()`, `nfs_pageio()`, `nfs_map()`, `nfs_addmap()`, `nfs_delmap()`, and `nfs_delmap_callback()`.
- Locking and metadata support includes `nfs_fid()`, `nfs_rwlock()`, `nfs_rwunlock()`, `nfs_seek()`, `nfs_frlock()`, `nfs_space()`, `nfs_pathconf()`, `nfs_setsecattr()`, `nfs_getsecattr()`, and `nfs_shrlock()`.

## Internal Mechanics
The file translates vnode operations into NFSv2 RPCs using `rfs2call()` and XDR helpers. Most operations enforce zone ownership before wire I/O. Rnode state locks protect cached size, attributes, symlink contents, readdir cache state, pending writes, mmap counts, stale state, delayed errors, and temporary unlink names.

Read/write paths choose between direct RPC buffers and VM-cached segmap/VPM operation. Direct I/O is used for `VNOCACHE`, per-rnode direct I/O, mount direct I/O, or when no mappings/cached pages exist. Cached writes throttle dirty page creation based on async queue pressure and active getattr pagewalks.

`nfsread()` issues chunked `RFS_READ` calls, updates I/O kstats, zero-residual handling through callers, and compares returned attributes against cache state without forcing a cache purge while pages are locked. `nfswrite()` issues chunked synchronous `RFS_WRITE` calls, updates kstats, purges attributes, and sets `RWRITEATTR` so close can refresh attributes not returned by WRITE.

Directory operations carefully maintain DNLC and readdir caches. Creates handle NFSv2 special-file encoding by packing device numbers into mode/size fields. Remove and rename implement local unlink-open semantics by renaming active files to generated `.nfs*` names and recording cleanup data in the rnode for `nfs_inactive()`.

`nfs_readdir()` uses an AVL-backed `rddir_cache` keyed by server cookie and request size. It supports waiters on in-progress cache fills, async readdir readahead, EOF cookie short-circuiting, and cache invalidation on directory mutations. `nfsreaddir()` fills cache entries from `RFS_READDIR`.

The VM path uses `nfs_bio()` as the common page I/O bridge. `nfs_getapage()` clusters reads, handles EOF and zero-fill cases, and schedules async readahead using `nfs_nra`. `nfs_putapage()` clusters writes, detects `RMODINPROGRESS` races with `writerp()`, and either schedules async writeback or performs synchronous writeback. Out-of-space/quota/access errors set rnode state and may force invalidation retries.

Mmap support blocks mapping when direct/no-cache state or mandatory locks make caching unsafe. `nfs_delmap()` installs address-space callbacks so potentially slow NFS flush work runs without holding the address-space lock; the callback updates map counts and flushes or invalidates pages based on close-to-open/direct-I/O semantics.

Record locks use either local `fs_frlock()` for `MI_LLOCK` mounts or lock-manager calls with NFS file handles. Nonlocal locks flush/invalidate cached pages before setting/unsetting locks. Share reservations wrap local owner data with NFS owner magic and hostname before calling the lock manager.

## Dependencies
Depends on illumos VOP/VM/segmap/VPM/pageout infrastructure, rnode and mount state helpers, NFS async worker queues, DNLC, ACL v2 helpers, lock manager (`lm_*`), kstats, DTrace I/O probes, NFS failover helpers, vnode event notifications, and XDR routines in `nfs_xdr.c`.

## Risks and Notes
- Many paths depend on careful lock ordering between `r_rwlock`, `r_lkserlock`, `r_statelock`, page locks, and address-space locks.
- NFSv2 32-bit offset limits are enforced throughout; reads/writes/truncates beyond `MAXOFF32_T` fail.
- Delayed write errors are stored in `r_error` and surfaced later on close/fsync/page operations.
- The `.nfs*` temporary-name mechanism is central to POSIX unlink-open behavior over a protocol without native support.
- Readdir cookies are opaque server offsets; `lseek()` on directories intentionally allows these values.
