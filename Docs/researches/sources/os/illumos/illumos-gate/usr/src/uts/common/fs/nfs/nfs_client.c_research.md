# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_client.c

## Purpose

`nfs_client.c` contains shared illumos NFS client support used by the NFSv2 and NFSv3 client implementations. It is not a vnode-op table itself; it provides common cache validation, attribute caching, page-cache invalidation, async I/O queues, mount lifecycle cleanup, lock-manager cleanup, kstats, and direct delmap bookkeeping.

The file is central to client correctness because it coordinates rnode state, VM cache state, NFS attribute freshness, async writeback, cross-zone teardown, and lock-manager uncertainty.

## Main Interfaces

Important cache and attribute functions:

- `nfs_validate_caches`, `nfs3_validate_caches`
- `nfs_waitfor_purge_complete`
- `nfs_purge_caches`, `nfs_purge_rddir_cache`
- `nfs_attr_cache`, `nfs3_cache_wcc_data`
- `nfs_attrcache`, `nfs3_attrcache`, `nfs_attrcache_va`
- `nfs_cache_fattr`, `nfs3_cache_fattr3`
- `nfs_getattr_otw`, `nfs3_getattr_otw`
- `nfsgetattr`, `nfs3getattr`
- `nattr_to_vattr`, `fattr3_to_vattr`

Important async and VM helpers:

- `nfs_async_manager`, `nfs_async_manager_stop`
- `nfs_async_readahead`
- `nfs_async_putapage`
- `nfs_async_pageio`
- `nfs_async_readdir`
- `nfs_async_commit`
- `nfs_async_inactive`
- `nfs_async_stop`, `nfs_async_stop_sig`
- `writerp`
- `nfs_putpages`
- `nfs_invalidate_pages`

Mount/module, zone, and statistics helpers:

- `nfs_clntinit`, `nfs_clntfini`
- `nfs_mi_zonelist_add`, `nfs_mi_zonelist_remove`
- `nfs_free_mi`
- `nfs_mnt_kstat_init`
- `mnt_kstat_update`

Locking and mapping helpers:

- `nfs_lockrelease`
- `nfs_lockcompletion`
- `nfs_add_locking_id`
- `nfs_remove_locking_id`
- `nfs_init_delmapcall`
- `nfs_find_and_delete_delmapcall`
- `nfs_free_delmapcall`

## Cache And Attribute Model

Attribute caching is adaptive. `nfs_attrcache_va()` stores the returned `vattr_t`, computes an expiration time from how recently file data changed, and clamps that time by mount options such as `acregmin`, `acregmax`, `acdirmin`, and `acdirmax`. `MI_NOAC` and `VNOCACHE` force immediate expiration.

`nfs_attr_cache()` and `nfs3_attr_cache()` compare new server attributes against cached rnode state. If mtime, ctime, or size indicates a change, they purge page data, readlink cache, readdir cache, DNLC entries as needed, access cache, and cached ACL/security attributes.

Cache purge is serialized through `rp->r_serial` and `RINCACHEPURGE` so another thread cannot observe an updated file size and then read stale or zero-filled cached pages while invalidation is still in progress. `nfs_waitfor_purge_complete()` lets fast-path cache validation wait for that purge to complete.

`nfs3_cache_wcc_data()` uses NFSv3 weak cache consistency data. If before and after attributes are both available, it validates against the pre-operation values and then caches the after values. If post-operation attributes are missing, it expires the attribute cache.

## Attribute Conversion

`nattr_to_vattr()` converts NFSv2 wire attributes into illumos `vattr_t`, including NFS nobody uid/gid mapping, vnode type mapping, NFSv2 device-number expansion, FIFO compatibility handling, time conversion, and 32-bit time overflow checks.

`fattr3_to_vattr()` performs the NFSv3 equivalent, including large-file checks with `NFS3_SIZE_OK`, vnode type mapping, `makedevice()` for special files, block count calculation from `used`, and 32-bit time overflow checks.

Both conversion paths deliberately keep the remote file size in the temporary `vattr_t` for cache validation, while `nfsgetattr()` and `nfs3getattr()` finally return the client-side `rp->r_size` view to callers.

## Async I/O Model

The async subsystem is per mount. `nfs_async_manager()` owns worker creation and shutdown. Work is queued by operation type, and workers process queues round-robin with clustering counters so a run of write-like operations can be serviced together.

Supported async request types include readahead, putapage, pageio, readdir, commit, and inactive cleanup. The queue state is protected by `mi_async_lock`; rnode active I/O counters are tracked with `r_count` and `r_awcount`.

The manager thread exists partly for zone correctness. Global-zone pageout and fsflush can need to initiate work against an NFS mount in another zone, but cross-zone direct NFS calls are disallowed. The async manager and workers run in the mount’s zone and drain work before zone or unmount teardown.

Fallback behavior is conservative:

- If async allocation fails for readahead, it simply skips readahead.
- If async putpage/pageio cannot run from pageout or fsflush, dirty pages are re-marked rather than doing blocking network I/O in those contexts.
- If cross-zone synchronous page writeback would be required, pages are unlocked with error handling instead of issuing the call from the wrong zone.
- `nfs_async_commit()` re-marks pages as needing commit if commit cannot be safely sent from the current context.

## VM And Page Cache Behavior

`writerp()` moves user data into cached pages in page-sized chunks while holding the NFS write lock. It sets `RMODINPROGRESS` while the last-page contents and `r_size` are in flux, preventing pageout from writing an incorrectly sized EOF page. After `uiomove()` or `vpm_data_copy()`, it updates `r_size`, clears `RMODINPROGRESS`, and marks `RDIRTY`.

`nfs_putpages()` writes or invalidates dirty cached pages over a range or whole file. It forces invalidation when `ROUTOFSPACE` is set or the VFS is unmounted. It carefully clears and restores `RDIRTY` around full-file flushes so concurrent dirtying is not lost.

`nfs_invalidate_pages()` serializes truncation/invalidation with `RTRUNCATE`, records the truncation address, invalidates pages via `pvn_vplist_dirty()`, and wakes waiters afterward.

## Zone And Mount Lifecycle

The file uses a per-zone `mi_globals` list of NFS mounts. `nfs_mi_shutdown()` walks that list during zone shutdown, purges DNLC entries for each filesystem, disables async thread creation, wakes async workers, sets `MI_ASYNC_MGR_STOP`, and marks mounts `MI_DEAD`.

`nfs_mi_destroy()` defers freeing per-zone state if VFS cleanup has not yet removed all mounts. `nfs_mi_zonelist_remove()` completes that deferred cleanup after the last mount disappears.

`nfs_free_mi()` asserts async manager and workers are stopped, removes the mount from the zone list, releases lock-manager config, destroys locks and condition variables, destroys rnode lists, releases the zone reference, and frees `mntinfo_t`.

## Lock Manager Integration

`nfs_lockrelease()` is called when closing a vnode to release remote locks and share reservations held by the current process. It uses the local `r_lmpl` list to detect lock-manager uncertainty: if the client may be out of sync with the server, it issues an unlock for the whole file even if local lock state is not definitive.

`nfs_add_locking_id()` records uncertain lock or share ownership in the rnode. `nfs_remove_locking_id()` removes matching entries and optionally returns share-owner data for `F_UNSHARE`.

`nfs_lockcompletion()` updates `VNOCACHE` depending on whether the lock manager says cached mapping is safe. It also purges attributes after lock acquisition because open-time attributes may already be stale.

## Diagnostics And Kstats

`nfs_write_error()` rate-limits ENOSPC and EDQUOT console messages per mount and prints filehandle data using `nfs_printfhandle()`. It suppresses output during forced unmount or zone shutdown to avoid console flooding.

`nfs_mnt_kstat_init()` creates per-mount NFS I/O and `mntinfo` kstats. `mnt_kstat_update()` reports protocol, version, flags, security mode, transfer sizes, retransmission settings, attribute-cache timers, timeout estimator state, failover counters, remap counters, and current server hostname.

## Notable Invariants

- Attribute cache validation and data-cache invalidation are serialized through `r_statelock`, `r_serial`, and `RINCACHEPURGE`.
- `rp->r_mtime` is a client-side “last detected change” time, not a direct server timestamp comparison.
- `r_size` is the client’s authoritative local size view while dirty cached data exists.
- Async work queues are per mount and drained before unmount or zone teardown completes.
- Pageout/fsflush paths avoid blocking synchronous network writes when async dispatch is unavailable.
- Lock-manager uncertainty is stored per rnode and cleaned up on close.
- Cross-zone NFS operations are avoided or deferred through async mount-zone workers.

## Dependencies

This file depends on:

- NFS/rnode definitions from `nfs_clnt.h`, `rnode.h`, `nfs.h`, `nfs_acl.h`, and `lm.h`
- NFSv2 and NFSv3 RPC helpers such as `rfs2call`, `rfs3call`, `nfslookup`, `nfs3lookup`, `geterrno`, and `geterrno3`
- VM and segmap APIs: `pvn_*`, `page_*`, `segmap_*`, `vpm_data_copy`
- DNLC APIs and vnode page-cache helpers
- Zone APIs and kernel thread creation
- Kstat APIs
- Lock-manager APIs such as `lm4_frlock`, local lock registration, and share locking

## Research Notes

This file is a shared correctness layer under the version-specific NFS client code. The most important audit areas are cache purge serialization around file-size changes, async writeback fallback behavior, cross-zone inactive/writeback handling, `RMODINPROGRESS` races, delayed write error reporting, and lock-manager uncertainty cleanup.
