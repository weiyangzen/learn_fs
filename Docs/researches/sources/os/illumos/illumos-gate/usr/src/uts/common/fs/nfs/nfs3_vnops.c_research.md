# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vnops.c

## Purpose

`nfs3_vnops.c` is the illumos NFSv3 client vnode operation implementation. It maps VFS/VOP calls onto NFSv3 RPCs, VM/page-cache operations, name cache maintenance, lock-manager integration, ACL/security hooks, and close-to-open consistency behavior.

The exported operation table is `nfs3_vnodeops_template`, with `nfs3_getvnodeops()` returning the installed `struct vnodeops *`. The file is central to the NFSv3 client because it bridges local vnode semantics and remote NFS protocol behavior.

## Main Interfaces

The VOP entry points include:

- File lifecycle and I/O: `nfs3_open`, `nfs3_close`, `nfs3_read`, `nfs3_write`, `nfs3_ioctl`, `nfs3_fsync`
- Attributes and permissions: `nfs3_getattr`, `nfs3_setattr`, `nfs3_access`, `nfs3_setsecattr`, `nfs3_getsecattr`, `nfs3_pathconf`
- Namespace operations: `nfs3_lookup`, `nfs3_create`, `nfs3_remove`, `nfs3_link`, `nfs3_rename`, `nfs3_mkdir`, `nfs3_rmdir`, `nfs3_symlink`, `nfs3_readlink`, `nfs3_readdir`
- VM integration: `nfs3_getpage`, `nfs3_putpage`, `nfs3_pageio`, `nfs3_dispose`, `nfs3_map`, `nfs3_addmap`, `nfs3_delmap`
- Locking and share reservations: `nfs3_frlock`, `nfs3_shrlock`, `nfs3_rwlock`, `nfs3_rwunlock`
- Identity/utility: `nfs3_fid`, `nfs3_seek`, `nfs3_realvp`, `nfs3_inactive`

Important internal helpers include `nfs3read`, `nfs3write`, `nfs3_bio`, `nfs3_rdwrlbn`, `nfs3lookup_dnlc`, `nfs3lookup_otw`, `nfs3create`, `nfs3mknod`, `nfs3rename`, `do_nfs3readdir`, `nfs3readdir`, `nfs3readdirplus`, `nfs3_commit`, `nfs3_putpage_commit`, and commit-page gathering helpers.

## Behavior And Data Flow

Most vnode operations follow this pattern:

1. Validate the caller is in the mount's NFS zone.
2. Acquire rnode locks as needed.
3. Validate or purge local caches.
4. Build NFSv3 RPC argument structs.
5. Call `rfs3call()` with an XDR routine from `nfs3_xdr.c`.
6. Translate NFS status with `geterrno3()`.
7. Update attributes, weak cache consistency data, DNLC, readdir cache, page state, and vnode events.

The file uses `rnode_t` as the per-vnode state carrier. Key fields include cached attributes, size, access cache, readdir cache AVL tree, symlink cache, credential cache, error state, write verifier, dirty/commit flags, mmap count, outstanding async write count, and unlink-open cleanup state.

## Cache And Consistency Model

Open and close paths implement close-to-open consistency unless `MI_NOCTO` disables it. `nfs3_open()` validates caches or forces an over-the-wire `GETATTR` when mmap or cached data might be stale. `nfs3_close()` flushes dirty pages and commits unstable writes unless the mount is `nocto`, in which case it starts async writeback.

Attribute cache handling is pervasive:

- `PURGE_ATTRCACHE` is used after uncertain RPC outcomes, stale file handles, writes, removes, and rename-related uncertainty.
- `nfs3_cache_post_op_attr`, `nfs3_cache_post_op_vattr`, and `nfs3_cache_wcc_data` update attributes from NFS post-op or WCC data.
- `RWRITEATTR` marks that a WRITE changed server state and returned insufficient attributes, forcing later refresh.

The DNLC is used for positive and negative lookup caching. `nfs3lookup_dnlc()` validates directory caches before trusting DNLC entries. `nfs3lookup_otw()` performs actual LOOKUP RPCs and populates nodes/DNLC. Negative lookup caching is controlled by `nfs3_lookup_neg_cache`.

Directory read caching is an AVL-backed `rddir_cache` indexed by NFS cookie and request length. `nfs3_readdir()` can use cached results, wait for in-progress fills, trigger asynchronous readahead, and choose READDIRPLUS when previous lookup behavior suggests it will help populate DNLC.

## File I/O And VM Integration

`nfs3_read()` and `nfs3_write()` prefer VM/segmap cached I/O, but bypass VM for `VNOCACHE`, per-rnode direct I/O, mount-level direct I/O, or non-mapped files without cached pages. Direct read uses `nfs3_directio_read()`, decoding directly into the caller's `uio`.

Cached reads call `nfs3_validate_caches()`, map file pages with `vpm_data_copy()` or `segmap_getmapflt()`, and release pages with `SM_DONTNEED` when appropriate.

Cached writes enforce append serialization, file-size limits, async write throttling, and use `writerp()` to dirty page-cache data. `nfs3_write()` forces synchronous writeback for `FSYNC`, `FDSYNC`, `MI_NOAC`, swap vnodes, or out-of-space state.

`nfs3_getpage()` and `nfs3_getapage()` handle page faults and readahead. They use `pvn_getpages`, `pvn_read_kluster`, `pageio_setup`, and `nfs3_bio()` to fetch pages. EOF is represented internally with `NFS_EOF`.

`nfs3_putpage()` and `nfs3_putapage()` handle writeback, clustering, async putpage, and page invalidation. The `RMODINPROGRESS` check prevents data loss when pageout races with a write whose `r_size` update has not completed.

## Stable Writes And COMMIT

The file implements full NFSv3 unstable write handling:

- `nfs3_rdwrlbn()` chooses `UNSTABLE` writes for async writeback when memory pressure allows, marking pages with `C_DELAYCOMMIT`.
- `nfs3write()` sends WRITE RPCs, checks returned counts, tracks server write verifier changes, and purges attributes.
- `nfs3_commit()` sends COMMIT RPCs and compares returned verifier against `rp->r_verf`.
- Verifier mismatches call `nfs3_set_mod()` to mark pages dirty again and return `NFS_VERF_MISMATCH`.
- `nfs3_putpage_commit()` loops: async flush, sync flush, verify write verifier, then commit pages; on verifier mismatch it restarts.
- `nfs3_dispose()` batches commit-needed pages before freeing or destroying them, and can defer commit from pageout/fsflush or cross-zone context through `nfs_async_commit()`.

This write verifier machinery is one of the highest-risk areas in the file because correctness depends on preserving dirty data across server reboots or unstable-write loss.

## Namespace Operations

`nfs3_create()` avoids trusting DNLC for existence decisions and uses guarded CREATE for non-exclusive creates to avoid retransmitted truncation. Exclusive creates generate a verifier and may follow with SETATTR to set final attributes/times.

`nfs3_remove()` implements unlink-open semantics by renaming active files to temporary `.nfs*` names and storing cleanup state in the rnode. `nfs3_inactive()` later removes these temporary names.

`nfs3rename()` handles target activity, mountpoint checks, unlink-open semantics for overwritten active targets, source/target directory lock ordering, DNLC invalidation, readdir cache purging, WCC updates, and vnode event emission. It maps NFS `ENOTEMPTY` to System V style `EEXIST`.

`nfs3_mkdir`, `nfs3_rmdir`, `nfs3_link`, `nfs3_symlink`, and `nfs3mknod` all update directory WCC data, purge readdir caches, adjust DNLC, and compensate for server behavior such as unsupported LINK/SYMLINK or differing group assignment.

## Locking, Mapping, And Zones

Zone checks guard nearly every operation. Synchronous operations return `EIO` or `EPERM` from the wrong zone. `nfs3_inactive()` and some async page cleanup paths can hand work to async workers when called from the wrong zone.

`nfs3_map()` coordinates `r_rwlock`, `r_lkserlock`, and `r_inmap` to prevent races between mmap, direct I/O, and remote locks. `nfs3_delmap()` uses address-space callbacks so NFS writeback/commit can happen after dropping the address-space lock. The callback updates map counts, flushes dirty shared writable mappings, and invalidates direct-I/O pages.

`nfs3_frlock()` rejects unsupported OFD/flock modes, validates byte ranges, delegates local-lock mounts to local locking, otherwise serializes with `r_lkserlock`, flushes/invalidate caches before locking or unlocking, and calls `lm4_frlock()`. `nfs3_shrlock()` similarly integrates with local share reservations or remote lock manager share calls.

## Security And ACLs

`nfs3_setattr()` calls `secpolicy_vnode_setattr()` before issuing SETATTR. Mode/owner/group changes purge the NFS access cache and ACL cache. `nfs3_access()` translates VFS access bits to NFSv3 ACCESS bits, handles readonly checks, consults per-rnode access cache, and retries with network-adjusted credentials from `crnetadjust()`.

ACLs are delegated to `acl_setacl3()` and `acl_getacl3()` when mount flag `MI_ACL` is still active; otherwise `nfs3_getsecattr()` falls back to fabricated ACLs through `fs_fab_acl()`.

## Notable Invariants

- NFS RPCs that touch a mount generally require `nfs_zone() == mi_zone`.
- `r_rwlock` serializes high-level vnode operations such as create/remove/rename/readdir and append writes.
- `r_lkserlock` serializes locking with mmap/direct I/O decisions.
- `RCOMMIT` serializes use of the rnode commit page list.
- `r_count`, `r_awcount`, and `r_gcount` throttle or synchronize pageout, writes, and getattr-triggered flushes.
- `rp->r_error` stores async writeback errors until close/fsync-style consumers retrieve them.
- DNLC and readdir caches are purged after namespace mutations or stale/uncertain outcomes.
- `p_fsdata` tracks whether a page needs COMMIT after unstable writes.

## Dependencies

This file depends heavily on:

- NFS client state and RPC helpers from `nfs_clnt.h`, `rnode.h`, and related NFS code.
- XDR routines in `nfs3_xdr.c`, such as `xdr_READ3args`, `xdr_READ3vres`, `xdr_WRITE3args`, `xdr_WRITE3res`, `xdr_READDIR3vres`, and `xdr_COMMIT3res`.
- VM/page-cache APIs: `segmap`, `vpm`, `pvn_*`, `page_*`, `hat_*`, `pageio_setup`.
- DNLC and vnode event APIs.
- Lock-manager functions: `lm4_frlock`, `lm4_shrlock`, `nfs_lockrelease`, `nfs_lockcompletion`.
- ACL helpers: `acl_getacl3`, `acl_setacl3`, `acl_getxattrdir3`.

## Research Notes

This is not just an RPC wrapper. It encodes the client-side semantics that make NFSv3 behave like a local filesystem under VFS: close-to-open cache consistency, unlink-open behavior, memory mapped writeback, unstable write commit, negative lookup caching, READDIRPLUS DNLC population, ACL fallback, lock-cache interaction, and cross-zone cleanup behavior.

Potential audit hotspots are write verifier mismatch handling, `RMODINPROGRESS` writeback races, unlink-open rename cleanup, `nfs3_delmap()` callback flow, direct I/O cache invalidation, and any paths that update `rp->r_error` asynchronously.
