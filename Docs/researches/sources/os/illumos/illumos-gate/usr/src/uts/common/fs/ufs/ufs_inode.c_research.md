# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_inode.c

## Purpose

`ufs_inode.c` implements UFS in-core inode cache management, inode lookup/loading, inactive handling, inode writeback, truncation/block freeing, permission checks, inode scanning, and timestamp maintenance. It is the main bridge between on-disk `dinode` records and live UFS `inode`/`vnode` objects.

It also initializes several global UFS facilities: inode kstats, idle/delete queue thresholds, inode hash tables, quota support, fix-on-panic support, shadow inode cache, direct I/O, and logging.

## Main Interfaces

Public entry points include:

- `ufs_iinit()` initializes inode subsystem state, queues, kstats, and related UFS modules.
- `ufs_alloc_inode()` and `ufs_free_inode()` allocate/free in-core inode objects.
- `ufs_iget()` returns a held inode by inode number.
- `ufs_iget_alloced()` is the stricter lookup variant that rejects free/unlinked inodes.
- `ufs_reset_vnode()` derives vnode flags from inode mode/type.
- `ufs_iinactive()` handles last-reference inactive processing.
- `ufs_iupdat()` writes dirty inode fields to disk or the transaction log.
- `ufs_itrunc()` grows or truncates file storage and frees blocks.
- `ufs_iaccess()` performs read/write/execute permission checks.
- `ufs_rmidle()` removes an inode from idle queues.
- `ufs_scan_inodes()` walks the inode hash and calls a callback safely.
- `ufs_imark()` and `ufs_itimes_nolock()` maintain unique timestamps.

Private helpers include `ufs_inode_kstat_update()`, `ufs_inode_cache_constructor()`, `ufs_inode_cache_destructor()`, `ihinit()`, `ufs_iget_internal()`, and `indirtrunc()`.

## Inode Cache And Lookup

`ufs_iinit()` validates write-throttling tunables (`ufs_HW`, `ufs_LW`), bounds `ufs_ninode`, computes idle queue limits, starts idle and hlock threads, initializes hash tables, quotas, fix-on-panic, shadow inode cache, direct I/O, and logging. It installs the `ufs/inode_cache` kstat.

The inode kmem constructor allocates a vnode, assigns UFS vnodeops, initializes `i_rwlock`, `i_contents`, `i_tlock`, directory DNLC anchor, and write CV. `ufs_alloc_inode()` resets per-inode fields, associates the vnode with the mount, sets `VROOT` for the root inode, and calls `vn_exists()`.

`ufs_iget_internal()` first searches the inode hash by device and inode number, ignoring stale inodes. Cache hits take a vnode hold, remove the inode from idle queues if needed, reset vnode flags, and return. Cache misses allocate a placeholder inode, insert it into the hash under lock, read the on-disk dinode, copy `di_ic`, restore old 16-bit UID/GID compatibility fields, decode device numbers, set vnode type, load shadow ACL state when present, attach quotas when appropriate, and call `TRANS_MATA_IGET()`.

The `validate` mode used by `ufs_iget_alloced()` rejects type-zero or unlinked inodes, marks them stale, releases them, and logs a note recommending fsck.

## Inactive And Queue Handling

`ufs_iinactive()` runs when the vnode is no longer referenced. It purges directory DNLC state, takes `i_contents` writer, rechecks `v_count` under vnode lock, and handles three broad cases:

- Inodes from a forcibly unmounted filesystem (`i_ufsvfs == NULL`) are unhashed/clean and can be freed directly.
- Writable unlinked inodes are deleted immediately on non-logging filesystems or queued to the mount delete thread under logging, unless lockfs has `NOIDEL`.
- Other inodes go to idle queues. Inodes with pages or fast symlinks go to useful idle queues; others go to junk queues and get `IJUNKIQ`.

`ufs_rmidle()` removes an inode from idle queues, restores `IREF`, and updates useful/junk queue counters. `ufs_scan_inodes()` walks every hash chain while taking vnode holds only for inodes in the requested filesystem, drops hash locks around callback work, and optionally try-locks inode contents to avoid blocking.

## Inode Update And Timestamping

`ufs_iupdat()` writes dirty inode metadata. It skips forcibly unmounted or stale inodes, ignores writes on read-only filesystems after clearing dirty flags, calls `ufs_notclean()`, reads the containing inode block, applies `ITIMES_NOLOCK()`, logs access-time-only deltas when needed, updates legacy UID/GID and device-number encodings, copies `i_ic` into the dinode, clears unused fast-symlink block pointers, and either logs the dinode sector or writes the buffer synchronously/asynchronously.

If a prior asynchronous inode update left `IBDWRITE`, a later synchronous request flushes the inode block even if no new flags are set.

`ufs_imark()` maintains monotonically unique 32-bit UFS timestamps protected by `ufs_iuniqtime_lock`, clamps at `TIME32_MAX`, increments `i_seq` for deferred sequence updates, updates atime/mtime/ctime according to `IACC`, `IUPD`, and `ICHG`, and resets `i_diroff` on ctime changes. `ufs_itimes_nolock()` converts pending timestamp flags into `IMOD` or `IMODACC` unless noatime suppresses an access-only update.

## Truncation And Block Freeing

`ufs_itrunc()` supports regular files, directories, attribute directories, zero-length symlinks, and shadow inodes. It checks max file size, handles free-time generation updates, clears fast-symlink state, grows files through `BMAPALLOC()`, zeroes bytes beyond old EOF on growth, sets large-file superblock state, and returns after successful extension.

For shrinking, it invalidates or zeroes pages beyond the new EOF, ensures the partial final block is allocated and resident so `pvn_vpzero()` can clean it, writes the shortened inode before freeing blocks, and then frees indirect and direct blocks in reverse order. `indirtrunc()` recursively cleans indirect blocks, logging zeroed pointer ranges before freeing child blocks.

The truncation code keeps a temporary copy of the old inode block pointers, clears pointers in the real inode first, synchronously updates the inode when not logging, frees blocks from the copy, verifies real and copy pointers remain consistent, adjusts `i_blocks`, and updates quotas with negative block deltas.

## Permissions

`ufs_iaccess()` enforces read-only filesystem behavior for writes except character/block devices and FIFOs. If UFS ACL state is present, it delegates to `ufs_acl_access()`. Otherwise it selects owner/group/other bits based on credential UID and group membership and calls `secpolicy_vnode_access2()`.

## Invariants And Dependencies

Key invariants:

- Inode hash insertion uses a placeholder under `i_contents` writer so scanners and lookups see initialized state.
- `ISTALE` inodes are ignored by new lookups and eventually freed.
- Unlinked logged inodes are queued rather than deleted synchronously.
- Inode disk updates must preserve old UID/GID and device encoding compatibility.
- File shrinking writes the shortened inode before freeing blocks to remain crash-tolerant.
- Timestamps are unique within the filesystem's 32-bit on-disk time limits.

Dependencies include UFS buf I/O, page-cache invalidation and dirty walks, transaction logging, quotas, DNLC, ACL/shadow inode support, vnode lifecycle APIs, idle/delete thread queues, superblock clean-state helpers, and block allocator/free routines.

## Research Notes

This file is a major correctness center. The most important audit areas are stale inode races during lookup/inactive, queued delete behavior under lockfs/logging, `ufs_itrunc()` ordering, fast-symlink dinode sanitization, `IBDWRITE` synchronous flush semantics, and 2038-era timestamp clamping.
