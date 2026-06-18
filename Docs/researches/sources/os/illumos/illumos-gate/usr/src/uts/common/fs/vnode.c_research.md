# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vnode.c

## Purpose
`vnode.c` is the illumos kernel’s common vnode operation and lifecycle layer. It builds vnode operation vectors, implements generic open/create/link/rename/remove helpers, manages vnode allocation/recycling/reference release, wraps every VOP call with accounting/feature checks/credential mapping, maintains vnode path caches, implements shared vnode/VFS lock hashing, provides vnode-specific data storage, and supports vopstats/reparse helpers.

## Major Responsibilities
- Defines `vn_ops_table`, mapping named VOP operations into `vnodeops_t` offsets and default/error functions.
- Creates and frees vnode operation vectors with `vn_make_ops()` / `vn_freevnodeops()`.
- Initializes and manages the vnode kmem cache.
- Implements `vn_rdwr()`, `vn_openat()`, `vn_createat()`, `vn_linkat()`, `vn_renameat()`, and `vn_removeat()`.
- Handles vnode release variants: normal, DNLC-aware, stream-clearing, and async inactive dispatch.
- Maintains VFS/vnode mount locks through a hashed `rwstlock` table used by both vnode and VFS code.
- Implements VOP wrapper functions `fop_*()` called by `VOP_*` macros.
- Maintains vnode open counts, mmap counts, vopstats counters, DTrace probes, and cached vnode paths.
- Implements vnode event helper calls for FEM/event notification.
- Provides vnode-specific data key/value storage with destructors.
- Implements xvattr helpers and reparse-point marking/query support.

## Key Data and Globals
- `vn_ops_table`: operation translation table for all standard vnode operations.
- `vn_cache`: kmem cache for `vnode_t`.
- `iftovt_tab`, `vttoif_tab`: mode/vnode-type translation tables.
- `vopstats_fstype`, `vs_templatep`, `vskstat_tree`, `vsk_anchor_cache`, `vopstats_enabled`: vopstats/kstat infrastructure.
- `vn_vpath_empty`: shared empty path sentinel for vnode path caching.
- `max_vnode_path`: cap for cached path allocation, defaulting to four `MAXPATHLEN`s.
- `vn_vfslocks_buckets`: hashed lock table keyed by vnode or VFS pointer.
- `vsd_lock`, `vsd_nkeys`, `vsd_list`, `vsd_destructor`: vnode-specific data registry.

## Vopstats and Kstats
- `create_vopstats_template()` initializes all named counters once, including operation counts and byte counters for read/write/readdir.
- `initialize_vopstats()` copies the template into a per-VFS stats structure.
- `get_fstype_vopstats()` finds per-filesystem-type stats, accounting for NFS variants and special VFS instances.
- `get_vskstat_anchor()` uses `VFS_STATVFS()` fsid to create a per-mounted-filesystem kstat anchor in an AVL tree.
- `teardown_vopstats()` removes the anchor, deletes kstats, and frees anchor state.
- `VOPSTATS_UPDATE` and `VOPSTATS_UPDATE_IO` update per-mounted and per-fstype counters and fire fsinfo DTrace probes.

## Generic File Operations
- `vn_rdwr()` builds a single-iovec `uio`, checks read-only writes and negative lengths, applies NBMAND conflict checks, takes `VOP_RWLOCK()`, dispatches read/write, unlocks, and reports residuals.
- `vn_openat()` handles create vs lookup open, large-file checks, write/truncate restrictions, mandatory lock checks, access checks, `FNOFOLLOW`, `FNOLINKS`, socket restrictions, NBMAND share reservations, `VOP_OPEN()`, truncate via `VOP_SETATTR()`, direct I/O enablement, and ESTALE retry.
- `vn_createat()` resolves parent/target, applies default ACL/umask behavior, handles read-only and existing-file cases, mandatory lock truncation checks, mount-root special handling, large-file overflow checks, mkdir/create dispatch, audit hooks, and ESTALE retry.
- `vn_linkat()` resolves source and target parent, verifies same fsid and writable target filesystem, then calls `VOP_LINK()`.
- `vn_renameat()` resolves both parents/targets, verifies same fsid, rejects directory mount-root rename, checks NBMAND conflicts for source/target, and calls `VOP_RENAME()`.
- `vn_removeat()` resolves parent/entry, rejects mounted roots unless `VFS_UNLINKABLE`, handles namefs unmount-over-file behavior, checks parent VFS read-only state, performs NBMAND remove checks, and calls `VOP_RMDIR()` or `VOP_REMOVE()`.

## Vnode Lifecycle
- `vn_rele()` calls `VOP_INACTIVE()` when dropping the final reference, leaving `v_count` at 1 during inactive to prevent races.
- `vn_rele_dnlc()` treats multiple DNLC holds as one vnode reference through `v_count_dnlc`.
- `vn_rele_stream()` clears `v_stream` under `v_lock` before release.
- `vn_rele_async()` dispatches final inactive work to a taskq.
- `vn_recycle()` clears reusable vnode state: open/mmap counts, FEM head, cached path, file-event data, MPSS data, and VSD.
- `vn_reinit()` resets core vnode fields but preserves synchronization objects, `v_data`, and `v_op`.
- `vn_alloc()` allocates from `vn_cache` and reinitializes; `vn_free()` validates lock state/counts, frees path/FEM/file-event/VSD state, and returns to cache.
- `vn_reclaim()`, `vn_idle()`, `vn_exists()`, and `vn_invalid()` forward vnode state transitions to VFS FEM hooks when installed.

## Shared Vnode/VFS Locks
- `vn_vfslocks_getlock()` hashes an arbitrary vnode/VFS pointer to a bucket, finds or allocates a lock entry, and references it.
- `vn_vfslocks_rele()` decrements the refcount, removes zero-ref entries, destroys the rwst lock, and panics on invalid negative/not-found states.
- `vn_vfswlock_wait()`, `vn_vfsrlock_wait()`, `vn_vfswlock()`, `vn_vfsrlock()`, `vn_vfsunlock()`, and `vn_vfswlock_held()` protect `v_vfsmountedhere` and are also used by `vfs.c` for VFS locking.
- The lock release protocol intentionally drops two references: one temporary lookup reference and one lock-holder reference.

## VOP Wrapper Layer
The `fop_*()` wrappers are the common path behind `VOP_*` macros. They:
- Dispatch through `vp->v_op`.
- Map credentials with `VOPXID_MAP_CR()` when the filesystem lacks `VFS_XID`.
- Update vopstats after each operation.
- Gate feature-specific behavior, including case-insensitive lookup, dirent flags, ACL-on-create, xvattr, ACE-mask access, and zero-copy buffers.
- Maintain path cache updates on successful lookup/create/mkdir and path copying if `VOP_OPEN()` swaps vnodes.
- Maintain regular-file read/write open counts in `fop_open()` and `fop_close()`.
- Maintain mmap read/write page counts in `fop_addmap()` and `fop_delmap()`, including NFS `EAGAIN` delayed-delmap behavior.
- Validate dump block arguments before `vop_dump()`.
- Mark symlink creates as reparse points when the filesystem supports reparse data and the target uses the reparse tag format.

## Path Cache
- `vn_clearpath()` clears cached path conditionally by timestamp.
- `vn_setpath_common()` is the core path installer for direct strings, parent/name composition, and rename updates.
- `vn_updatepath()` updates child paths from parent lookup when safe and meaningful.
- `vn_setpath_str()` installs a complete root-relative path, used by VFS root handling.
- `vn_renamepath()` forces path update during filesystem rename.
- `vn_copypath()` copies an existing path to a newly returned vnode, mainly after `VOP_OPEN()` substitution.
- The implementation uses `v_path_stamp` to avoid replacing newer path data after lock drops and avoids updating paths through `VTRAVERSE` parents.

## Vnode Events and Accessors
- `vnevent_*()` helpers call `VOP_VNEVENT()` only when a vnode has FEM/event state.
- Accessors report read-only state, flock presence, mandatory locks, cached data, mountpoint status, mounted VFS, DNLC references, open modes, mapped modes, and zone-change safety.
- `vn_can_change_zones()` resolves real vnode, checks backing filesystem `vfssw` flags, and blocks zone movement for `VSW_NOTZONESAFE` filesystems unless `nfs_global_client_only` is set.

## Vnode-Specific Data
- `vsd_create()` allocates a global key and optional destructor, growing the destructor table as needed.
- `vsd_destroy()` clears a key globally and calls its destructor on every vnode that has a value.
- `vsd_get()` / `vsd_set()` access per-vnode values under `v_vsd_lock`.
- `vsd_free()` destroys all values attached to a vnode, unlinks its VSD node from the global list, and frees storage.
- `vsd_realloc()` is a zeroing grow/copy/free helper.

## Reparse and Extended Attributes
- `xva_init()` initializes an extensible attribute request structure.
- `xva_getxoptattr()` returns optional xvattr storage when `AT_XVATTR` is set.
- `fs_reparse_mark()` validates a reparse target and marks the symlink create attributes with `XAT_REPARSE`.
- `vn_is_reparse()` queries a symlink’s xvattr reparse bit when the filesystem supports xvattrs.

## Risks and Invariants
- Final vnode release depends on `VOP_INACTIVE()` tolerating the vnode still having `v_count == 1`.
- `vn_openat()` and `vn_createat()` have many multi-resource exits; correctness depends on paired close/unshare/VN_RELE/nbl_end paths.
- `fop_open()` increments counts before filesystem open to avoid false-negative open-count races, then must adjust counts if open fails or swaps vnodes.
- Path-cache code allocates while locks are dropped and relies on stamps to avoid stale overwrites.
- `vn_vfslocks_getlock()` can race allocation; the second bucket scan is required to avoid duplicate lock entries.
- `vsd_destroy()` assumes callers prevent concurrent `vsd_set()`/`vsd_get()` for the destroyed key.
- Feature gates intentionally fail early with `EINVAL`/`ENOTSUP` before calling filesystems that do not advertise support.
