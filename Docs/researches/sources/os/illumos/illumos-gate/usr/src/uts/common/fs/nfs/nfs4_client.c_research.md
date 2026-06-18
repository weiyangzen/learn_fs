# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client.c

## Purpose
Core support code for the illumos NFSv4 client. This file is not a single vnode operation table; it provides shared machinery used by the NFSv4 vnode layer, recovery layer, mount lifecycle, caching, async I/O, lease renewal, zone shutdown, shared filehandle management, and pathname tracking.

## Main Responsibilities
- Attribute-cache validation and invalidation.
- Page-cache flushing, dirty-page writeback, and truncation invalidation.
- Per-mount asynchronous request management and worker threads.
- Cross-zone-safe handling for async writeback and inactive processing.
- Mount kstats and recovery kstat setup.
- Zone lifecycle tracking for all NFSv4 mounts in a zone.
- NFSv4 client init/fini sequencing.
- Lease renewal thread and `RENEW` over-the-wire call.
- State reference accounting for open files requiring lease maintenance.
- Shared filehandle interning through a per-mount AVL tree.
- `nfs4_fname_t` tree management for reconstructing paths and component names.

## Attribute And Cache Flow
- `nfs4_validate_caches()` returns quickly if attributes are valid, otherwise fetches attributes via `nfs4_getattr_otw()`.
- `nfs4_getattr_cache()` copies cached vnode attributes only when `ATTRCACHE4_VALID()` succeeds.
- `nfs4_getattr_otw()` wraps `nfs4_getattr_otw_norecovery()` with `nfs4_start_fop()`, NFSv4 recovery handling, cache update, stale filehandle purge, and SECINFO restore checks.
- `nfs4_getattr_otw_norecovery()` constructs `{ CPUTFH, GETATTR }` and requests `NFS4_VATTR_MASK`, optionally OR-ing ACL attributes.
- `nfs4getattr()` returns the rnode cache view after forcing a refresh if needed, and always reports client-side `r_size`.
- `nfs4_attr_otw()` is a generic attribute fetch helper using a caller-provided tag and bitmap.

`nfs4_attr_cache()` is the central cache coherency routine. It compares returned attributes and change information with rnode state, handles directory `change_info4`, tracks `R4WRITEMODIFIED`, serializes purge activity using `r_serial`, avoids deadlocks with page-flush threads, caches attributes through `nfs4_attrcache_va()`, and purges data/name/access/ACL caches when mtime, ctime, size, or change attributes indicate stale state.

`nfs4_attrcache_va()` computes adaptive attribute timeout windows using mount `ac*min/ac*max` settings, honors `MI4_NOAC` and `VNOCACHE`, updates `r_attr`, `r_change`, mounted-on fileid, pathconf cache, `r_size`, and swap-like state. It handles `NFS4_GETATTR_NOCACHE_OK` by forcing immediate invalidation.

## Page And Data Cache Handling
- `nfs4_purge_stale_fh()` marks `R4STALE`, records an rnode error, invalidates pages, and purges caches on `ESTALE`.
- `nfs4_purge_caches()` purges DNLC entries, symlink/readlink cache, xattr dir vnode, pathconf cache, page cache, and readdir cache. Page purge may be synchronous or delegated to `nfs4_pgflush_thread()`.
- `nfs4_waitfor_purge_complete()` waits for `r_serial` or `R4PGFLUSH` activity while respecting interruptible mounts.
- `nfs4_flush_pages()` issues `VOP_PUTPAGE(..., B_INVAL)` and records `ENOSPC`/`EDQUOT`.
- `nfs4_purge_rddir_cache()` resets directory EOF/lookup state and purges cached readdir data.
- `writerp4()` performs page-sized chunks of user-data copy into cached pages, manages page creation, `R4MODINPROGRESS`, `r_size`, and `R4DIRTY`.
- `nfs4_putpages()` writes or invalidates dirty pages for whole-file or range requests, preserving `R4DIRTY` on failed non-forced flushes.
- `nfs4_invalidate_pages()` serializes truncation/invalidation with `R4TRUNCATE`, updates `r_truncaddr`, calls `pvn_vplist_dirty()` with invalidation flags, then wakes waiters.

## Async I/O Model
The file implements a per-mount async manager to avoid illegal cross-zone NFS operations. Global-zone pageout/fsflush can enqueue work for a mount in another zone; the per-mount manager/worker threads execute the work in the correct context.

Key pieces:
- `nfs4_async_manager()` creates async worker or pageop worker threads as queued demand appears, drains work during shutdown, and exits only when `MI4_ASYNC_MGR_STOP` is set.
- `nfs4_async_common_start()` is the worker loop. It round-robins across async queues, honors cluster counts, performs the requested operation, frees request arguments, and exits after timeout or async shutdown.
- `nfs4_async_start()` and `nfs4_async_pgops_start()` select the normal or pageops queue.
- `free_async_args4()` releases vnode/credential references and decrements rnode I/O counters.
- `nfs4_async_stop()` and `nfs4_async_stop_sig()` disable async work and wait for worker/inactive quiescence, with the latter interruptible for unmount.

Queued operations include:
- `nfs4_async_readahead()`
- `nfs4_async_putapage()`
- `nfs4_async_pageio()`
- `nfs4_async_readdir()`
- `nfs4_async_commit()`
- `nfs4_async_inactive()`

Fallback behavior is carefully constrained. For pageout/fsflush or cross-zone synchronous fallback, dirty pages are normally re-marked or unlocked with error rather than performing unsafe synchronous NFS I/O in the wrong context.

## Inactive Handling
`nfs4_inactive_thread()` processes `NFS4_INACTIVE` queue entries until the async manager is gone and no inactive work remains. `nfs4_async_inactive()` must hand off inactive work for correctness. If the inactive thread is already unavailable, it performs local cleanup, drops delegations, clears open streams, and adds the rnode to the free list without doing unsafe over-the-wire work.

## Mount Kstats And Diagnostics
- `nfs4_mnt_kstat_update()` fills `mntinfo` raw kstat data: protocol, version, flags, negotiated/current security flavor, transfer sizes, retrans/timeo, attribute cache timers, server response/failover/remap counts, and current server name.
- `nfs4_mnt_kstat_init()` installs per-mount I/O kstats, read-only mount kstats, and recovery kstats.
- `nfs4_write_error()` rate-limits write error console messages, suppresses forced-unmount/recovery-failed spam, prints user/group information for `ENOSPC`/`EDQUOT`, and prints the filehandle.
- `nfs4_safemap()` checks active byte-range locks; only whole-file locks are considered mmap-safe.
- `nfs4_map_lost_lock_conflict()` checks queued lost `LOCK`/`LOCKU` requests for unsafe mmap conflicts.
- `nfs4_lockcompletion()` toggles `VNOCACHE` based on lock safety and purges attributes after lock acquisition.

## Zone And Mount Lifecycle
The file registers zone-specific mount globals using `zone_key_create()`:
- `nfs4_mi_init()` allocates a per-zone `mi4_globals` list.
- `nfs4_mi_zonelist_add()` inserts a mount and takes `mi`/`vfs` holds to avoid zone shutdown races.
- `nfs4_mi_shutdown()` walks zone mounts, purges DNLC, stops async/inactive threads, marks mounts dead, waits for recovery, removes mounts from the zone list, releases holds, and marks per-zone NFSv4 servers dead so renew threads exit.
- `nfs4_mi_destroy()` frees globals immediately or defers if mounts still await `VFS_FREEVFS()`.
- `nfs4_mi_zonelist_remove()` removes a mount unless shutdown already marked it dead.
- `nfs_free_mi4()` performs final `mntinfo4_t` teardown: kstats, debug message queue, names/filehandles, servinfo, locks/cvs/rwlocks, open-owner hash buckets, freed open-owner list, state/lost-state lists, rnode/filehandle containers, and the `mi` allocation.
- `mi_hold()`/`mi_rele()` implement `mntinfo4_t` reference counting.

## Client Init/Fini And CPR
`nfs4_clnt_init()` initializes NFSv4 vnode/rnode/shadow/access/subr/ACL/idmap/callback/SECINFO subsystems, installs a CPR callback, creates zone mount keys, and initializes the special unsupported-xattr vnode. `nfs4_clnt_fini()` tears those down and removes the CPR callback.

`nfs4_client_cpr_callb()` records resume time on CPR resume. The renew thread uses this to detect that leases may need prompt renewal after suspend/resume.

## Lease Renewal And State Accounting
`nfs4_renew_lease_thread()` is per-server. It sleeps based on lease time, propagation delay, state reference count, and lease validity. It renews only when state exists and the lease is valid, exits when marked, and waits for outstanding over-the-wire calls before releasing server references.

`nfs4renew()` sends `{ RENEW }`, updates propagation delay, handles `NFS4ERR_CB_PATH_DOWN` by returning all delegations while treating the lease as renewed, invokes recovery when needed, and handles status-to-errno conversion.

State ref helpers:
- `nfs4_inc_state_ref_count()` / `_nolock()` bump server state refs and mount open-file count, initialize lease validity, and reset renewal time when the first state appears.
- `nfs4_dec_state_ref_count()` / `_nolock()` decrement counts and may remove a mount from the server on last close when `MI4_REMOVE_ON_LAST_CLOSE` is set.
- `inlease()` checks current lease validity against last renewal time.
- `nfs4_server_in_recovery()` reports whether server recovery lock is writer-held.

## Shared Filehandle Interning
The per-mount filehandle AVL tree ensures shared `nfs4_sharedfh_t` objects:
- `sfh4_createtab()` creates the AVL.
- `sfh4_get()` finds or creates a shared filehandle.
- `sfh4_put()` handles speculative allocation and insert under `mi_fh_lock`.
- `sfh4_hold()`/`sfh4_rele()` maintain refcounts and remove/free last references.
- `sfh4_update()` removes an object, updates the handle, reinserts it if no duplicate exists, and warns on duplicate handles for writable mounts.
- `sfh4_copyval()` and `sfh4_printfhandle()` expose/print handle contents.

## Filename Tree
`nfs4_fname_t` objects track path components and parent/child relationships:
- `fn_get()` returns an existing child with matching name and shared filehandle or removes stale mismatched children and creates a new entry.
- `fn_hold()`/`fn_rele()` refcount and recursively release parents without recursive C calls.
- `fn_name()` returns a copy of a single component.
- `fn_path()` walks parents and builds a filesystem-root-relative path.
- `fn_parent()` returns a held parent.
- `fn_move()` updates parent/name after rename, removing conflicting child entries under the new parent.

## Important Invariants
- Many cache functions require careful avoidance of deadlock between recovery, page flush, and start/end operation regions.
- `r_serial`, `R4PGFLUSH`, `R4INCACHEPURGE`, `R4MODINPROGRESS`, and `R4TRUNCATE` are coordination flags, not incidental state.
- Async request counters and vnode/credential references are paired in `free_async_args4()`.
- Zone shutdown owns a large part of mount/thread teardown; normal unmount must cooperate with that path.
- Shared filehandle and fname code assumes AVL uniqueness, but explicitly handles stale or duplicate cases caused by volatile filehandles or server-side rename behavior.
