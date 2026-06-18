# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_vnops.c

## Role

`ufs_vnops.c` is the main illumos UFS vnode-operations implementation. It binds UFS to the VFS/vnode layer through `ufs_vnodeops_template`, implementing open/close, read/write, namespace operations, attributes, ACLs, mmap/page-cache operations, dump support, polling, pathconf, and file locking.

The file is large because it sits at the intersection of:
- UFS inode and directory manipulation.
- VM/page-cache integration through `segmap`, `vpm`, `pvn`, and `pageio`.
- UFS logging transactions through `TRANS_*`.
- lockfs/quiesce behavior through `ufs_lockfs_*`.
- quota synchronization through `vfs_dqrwlock`.
- extended attributes, ACLs, snapshots, direct I/O, large files, and dump devices.

## Vnode Operation Registration

The file declares `struct vnodeops *ufs_vnodeops` and defines `ufs_vnodeops_template[]`, mapping VFS operation names to UFS implementations. Major handlers include:

- `ufs_open`, `ufs_close`
- `ufs_read`, `ufs_write`
- `ufs_ioctl`
- `ufs_getattr`, `ufs_setattr`, `ufs_access`
- `ufs_lookup`, `ufs_create`, `ufs_remove`, `ufs_link`, `ufs_rename`
- `ufs_mkdir`, `ufs_rmdir`, `ufs_readdir`, `ufs_symlink`, `ufs_readlink`
- `ufs_fsync`, `ufs_inactive`, `ufs_fid`
- `ufs_rwlock`, `ufs_rwunlock`, `ufs_seek`, `ufs_frlock`, `ufs_space`
- `ufs_getpage`, `ufs_putpage`, `ufs_map`, `ufs_addmap`, `ufs_delmap`
- `ufs_poll`, `ufs_dump`, `ufs_l_pathconf`, `ufs_pageio`, `ufs_dumpctl`
- `ufs_getsecattr`, `ufs_setsecattr`

Some operations are explicitly noted as not blocked by lockfs, such as open, close, inactive, rwlock/rwunlock, addmap/delmap, and poll.

## Read and Write Path

`ufs_read()` validates mandatory locks before entering lockfs, then uses `rdip()` for actual reads. Directory reads receive special lock ordering to avoid deadlock with concurrent directory updates and synchronous-read logging. File reads may open a synchronous transaction for `FRSYNC` with `FSYNC` or `FDSYNC`.

`rdip()` performs the low-level read loop:
- Validates file type: regular file, directory, attribute directory, symlink, or shadow inode.
- Rejects negative offsets and handles EOF.
- Updates access time unless disabled by lockfs/noatime/read-only state.
- Attempts direct I/O first when `IDIRECTIO` or forced direct I/O is set.
- Uses `vpm_data_copy()` or `segmap_getmapflt()` plus `uiomove()` for buffered reads.
- Releases and reacquires `i_contents` around VM fault paths when safe.
- Supports POSIX sync-read behavior by pushing dirty pages on synchronous reads.

`ufs_write()` handles the high-level write protocol:
- Checks forced unmount and mandatory locks before lockfs/transaction entry.
- Detects concurrent direct-I/O rewrites with `ufs_check_rewrite()`.
- Allows a shared-lock direct-I/O rewrite fast path when the write does not extend the file, fill holes, append, or require full sync semantics.
- Upgrades `i_rwlock` to writer when the write is not safely concurrent.
- Reserves transaction space through `TRANS_WRITE_RESV()`.
- Throttles outstanding write bytes using `i_writes`, `ufs_HW`, `ufs_LW`, and `i_wrcv`.
- Uses `TRANS_WRITE()` when transaction residual handling is needed; otherwise calls `wrip()`.
- Retries once on `ENOSPC` after draining pending deletes when logging is active.

`wrip()` is the low-level write engine:
- Enforces file-size limits, large-file policy, negative offset rejection, and valid file types.
- Tries direct I/O first.
- Coordinates `vfs_dqrwlock` with block allocation and quota updates.
- Calls `bmap_write()` before extending files or allocating full mappings.
- Temporarily drops `i_contents` and sometimes `vfs_dqrwlock` around VM/page faultable copy paths.
- Uses `vpm_data_copy()` or `segmap_getmapflt()`, `segmap_pagecreate()`, `uiomove()`, and `segmap_release()`.
- Handles partially initialized pages by zeroing unwritten portions.
- Updates file size only after page creation/copy ordering allows it.
- Repairs file size through `ufs_itrunc()` on failed extending writes.
- Clears setuid/setgid bits after successful unprivileged writes when executable bits are present.
- Marks inode times and sequence changes, with special handling for sync writes and deferred inode updates.

## Attribute and Access Operations

`ufs_getattr()` has a fast path for `AT_SIZE`, otherwise reads inode fields under `i_contents`. It reports ACL mask-adjusted group permissions when a POSIX ACL mask exists, returns inode sequence number, timestamps, block size, block count, node ID, device IDs, and vnode type.

`ufs_setattr()` handles chmod/chown/truncate/timestamp updates:
- Rejects unsupported masks such as `AT_NOSET` and `AT_XVATTR`.
- Rejects read-only filesystems.
- Uses lockfs and transaction wrapping.
- Takes `i_rwlock` before transactions for non-directories and after transactions for directories, matching UFS operation ordering.
- Truncates through `TRANS_ITRUNC()`.
- Uses `secpolicy_vnode_setattr()` with `ufs_priv_access()` as the permission callback.
- Updates quota accounting on owner changes.
- Honors noatime behavior for atime-only updates.
- Updates ACL-related shadow inode state through `ufs_acl_setattr()`.
- Retries once after delete-queue draining on logged `ENOSPC`.

`ufs_access()` maps vnode permission bits directly to UFS inode permission bits and calls `ufs_iaccess()`.

## Ioctl Support

`ufs_ioctl()` implements UFS-specific control commands and quota control:
- `Q_QUOTACTL` under quota lockfs and quota transaction handling.
- `_FIOLFS` and `_FIOLFSS` for filesystem locking and lock status, with native and 32-bit structure translation.
- `_FIOSATIME`, `_FIOSDIO`, `_FIOGDIO`, `_FIOIO`, `_FIOFFS`, `_FIOISBUSY`.
- `_FIODIRECTIO`, `_FIOTUNE`, `_FIOLOGENABLE`, `_FIOLOGDISABLE`, `_FIOISLOG`.
- Snapshot creation/deletion commands.
- Superblock and maxphys queries.
- LUFS debug/error/statistics commands.
- Hole/data seek commands through `ufs_fio_holey()`.
- `_FIO_COMPRESSED`, marking files as compressed for dcfs layering.

The ioctl path is careful about forced unmount checks, privilege checks, copyin/copyout, lockfs masks, and transaction boundaries.

## Namespace Operations

`ufs_lookup()` handles regular and extended-attribute lookup:
- For `LOOKUP_XATTR`, validates mount support and prevents recursive attributes, then looks up or creates the hidden attribute directory using `ufs_xattr_getattrdir()`.
- Handles empty names and `"."` specially.
- Uses DNLC fast path where possible.
- Idles excess idle inodes before allocating more on lookup misses.
- Calls `ufs_diraccess()`, lockfs begin, and `ufs_dirlook()`.
- Converts device vnodes to specfs vnodes.
- Converts compressed files to dcfs vnodes through `decompvp()`.

`ufs_create()`:
- Wraps creation in lockfs and a create transaction.
- Handles null names as existing directory references.
- Uses DNLC and `ufs_direnter_cm()` for creation.
- Supports non-exclusive open of existing files, including optional truncation.
- Handles large-file overflow protection before truncating existing files.
- Returns specfs vnodes for device nodes.
- Defers parent directory sequence-number updates when lock ordering requires it.
- Retries once on logged `ENOSPC` after delete-queue draining.

`ufs_remove()` and `ufs_rmdir()`:
- Drain overly large pending-delete queues.
- Use `ufs_eventlookup()` before mutation to generate vnode events.
- Wrap directory removal in lockfs and transactions.
- Use `ufs_dirremove()` with operation-specific modes.

`ufs_link()`:
- Resolves real vnodes.
- Restricts hard links involving extended attributes so attribute entries link only within attribute directories.
- Enforces directory-link and basic-link privilege policy.
- Uses `ufs_direnter_lr()` inside lockfs and transaction handling.
- Emits link vnode events on success.

`ufs_rename()` is one of the most complex namespace operations:
- Performs event lookup before taking namespace locks.
- Uses lockfs and a rename transaction.
- Requires source and target parent directory inode types to match, including attribute-directory distinctions.
- Looks up the source inode and validates write/sticky permissions.
- Prevents invalid directory moves by checking that the target directory is not below the source.
- Uses reader locks on source and target directories for path checks, then upgrades to writer locks.
- Avoids deadlocks by retrying on failed trylocks, SLOCK conflicts, failed upgrades, or `ufs_dircheckpath()` `EAGAIN`.
- Links source to target with `ufs_direnter_lr(..., DE_RENAME, ...)`, then removes the source with `ufs_dirremove(..., DR_RENAME, ...)`.
- Emits pre/post rename vnode events for source, target, and destination directory.

`ufs_mkdir()` rejects creating directories inside attribute directories, then creates directories through `ufs_direnter_cm(..., DE_MKDIR, ...)`.

`ufs_symlink()` creates the symlink inode before inserting the directory entry to avoid races with `readlink()`. It writes symlink contents synchronously because symlink data is metadata. Small symlinks are cached in inode block fields as fast symlinks using `IFASTSYMLNK`.

`ufs_readlink()`:
- Rejects non-symlinks.
- Fast-returns empty symlinks.
- Reads fast symlinks directly from inode fields.
- For regular symlinks, may convert small symlinks into fast symlinks after reading, while avoiding user-buffer races by using a kernel buffer when needed.

`ufs_readdir()`:
- Validates offsets and iovec length.
- Reads directory blocks through `fbread()`.
- Converts UFS `struct direct` entries into `dirent64`.
- Skips empty entries and handles malformed directory records cautiously.
- Supports direct system-space output when possible, otherwise uses a temporary buffer and `uiomove()`.

`ufs_eventlookup()` is a helper used before remove/rmdir/rename event notifications. It validates name shape, parent execute/write access, DNLC lookup, idle queue pressure, lockfs, and `ufs_dirlook()`.

## Locking and Transaction Model

The file consistently coordinates three locking domains:
- `i_rwlock` for VOP-level read/write or namespace serialization.
- `i_contents` for inode metadata and file layout.
- `vfs_dqrwlock` for quota-sensitive block/inode accounting.

It also integrates lockfs:
- Most operations enter with `ufs_lockfs_begin()` using operation-specific masks.
- Some VM-sensitive paths use `ufs_lockfs_trybegin()` or `ufs_lockfs_begin_getpage()`.
- Deadlock-prone paths use trylocks and retry labels when SLOCK/quiesce interaction is possible.

Transactions are handled through `TRANS_BEGIN_*`, `TRANS_END_*`, and operation-size macros:
- Sync paths use `TRANS_BEGIN_SYNC()` or `TRANS_BEGIN_CSYNC()`.
- Async metadata/data operations use `TRANS_BEGIN_ASYNC()`.
- Page faults creating blocks can use `TRANS_TRY_BEGIN_ASYNC()` to avoid blocking non-kernel address spaces.
- Inode changes are recorded through `TRANS_INODE()`, `TRANS_IUPDAT()`, `TRANS_SYNCIP()`, and specialized macros.

ENOSPC handling in create/write/mkdir/symlink/setattr/setsecattr commonly drains the delete queue once when UFS logging is active.

## VM, Page Cache, and mmap

`ufs_getpage()` is optimized for page faults:
- Enforces lockfs getpage protocol.
- Starts transactions for write/create faults that may allocate blocks.
- Rejects `VNOMAP`.
- Handles EOF and hole behavior.
- Allocates blocks for holes on write/create faults through `bmap_write()`.
- Removes write permission from mappings of holey files for read faults to avoid later unsafe writes.
- Performs sequential read-ahead using `i_nextr` and `i_nextrio`.
- Uses `page_lookup()`, `ufs_getpage_miss()`, and page-list expansion.
- Updates atime unless suppressed.

`ufs_getpage_miss()` reads or creates a page:
- Creates zero pages for `S_CREATE`, UFS holes, or unwritten fallocate blocks.
- Uses `bmap_read()` and `pvn_read_kluster()` for real disk reads.
- Routes I/O through LUFS logging, snapshot strategy, or block-device strategy.
- Initiates read-ahead for sequential access.

`ufs_getpage_ra()` issues asynchronous clustered read-ahead, skipping direct-I/O files, holes, and fallocated blocks.

`ufs_putpage()` delays simple asynchronous clustered writes using `i_delayoff` and `i_delaylen`, flushing clusters on close or when non-contiguous/full.

`ufs_putpages()` flushes dirty pages over a range or whole vnode:
- Serializes against the vulnerable file-size extension window in `wrip()`.
- Avoids blocking async pageout when a writer is active.
- Uses `pvn_vplist_dirty()` or explicit page iteration.
- Clears `IMODTIME` after full-file sync.

`ufs_putapage()` writes one clustered set of dirty pages:
- Updates mmap-modified file times.
- Uses `bmap_read()` and refuses to allocate blocks.
- Handles UFS holes, fallocate block conversion, cluster construction, transaction deltas for shadow/quota inode data, snapshots/logging, write throttling, and async/sync completion.

`ufs_pageio()` supports lower-level page I/O, including segvn large-page fault paths:
- Handles VM page-size support cases.
- Respects quiesce/lockfs counters when possible.
- Uses trylocks for large-page faults to avoid inode/page lock-order deadlocks.
- Splits I/O by contiguous disk extents.
- Rejects holes for swap/pageio-style callers.
- Updates atime for large-page read faults.

`ufs_map()` implements mmap:
- Rejects `VNOMAP`, invalid offsets, non-regular files, and mandatory locked files.
- Takes address-space range lock.
- Uses `choose_addr()` and `as_map_locked()`.
- Acquires `as->a_lock` before lockfs to match page-fault ordering.
- Uses `ufs_lockfs_trybegin()` and retries without holding `a_lock` if lockfs would block.

`ufs_addmap()` and `ufs_delmap()` maintain `i_mapcnt`, which is used to reject mandatory file locks on mapped files.

## File Locking, Space, Poll, and Pathconf

`ufs_rwlock()` allows shared writer locks for direct-I/O rewrite cases when mandatory locking is not active; otherwise it takes exclusive locks. `ufs_rwunlock()` simply exits `i_rwlock`.

`ufs_frlock()` rejects mandatory record locking when the file is mapped, then delegates to `fs_frlock()`.

`ufs_space()` handles `F_FREESP` through `ufs_freesp()` and `F_ALLOCSP` through `ufs_allocsp()`, with lockfs masks for truncation and allocation. It emits truncate events when freeing from offset zero succeeds.

`ufs_poll()` reports regular-file readiness while rejecting epoll/edge-triggered usage via `fs_reject_epoll()` or `POLLET`. It reports hangup on forced unmount and errors for hard/error lockfs states.

`ufs_l_pathconf()` handles UFS-specific pathconf values:
- `_PC_NAME_MAX`
- `_PC_FILESIZEBITS`
- `_PC_XATTR_EXISTS`
- `_PC_ACL_ENABLED`
- `_PC_MIN_HOLE_SIZE`
- `_PC_SATTR_ENABLED`
- `_PC_SATTR_EXISTS`
- `_PC_TIMESTAMP_RESOLUTION`

For `_PC_XATTR_EXISTS`, it may find the attribute directory, test if it is empty, and unhook empty shadow directories through `ufs_unhook_shadow()` inside a transaction.

## fsync, inactive, fid, and rdwri

`ufs_fsync()` differs between logging and non-logging filesystems:
- With logging, it pushes data pages when needed, deltas delayed inode access-time updates, and commits a synchronous transaction if there are deltas.
- Without logging, it performs inode-only, data-sync, or full sync behavior depending on flags, then syncs indirect blocks.

`ufs_inactive()` delegates to `ufs_iinactive()`.

`ufs_fid()` fills `struct ufid` with inode number and generation for stable file handles.

`ufs_rdwri()` constructs a one-iovec `uio` and calls `wrip()` or `rdip()` for internal reads/writes.

## Dump Support

The file defines a private `struct dump` and global `dump_info`.

`ufs_dumpctl()`:
- `DUMP_ALLOC` snapshots a regular file’s direct and indirect disk-block mapping into memory after rejecting holey files.
- `DUMP_FREE` releases that mapping.
- `DUMP_SCAN` searches for contiguous filesystem blocks suitable for dump placement.

`save_dblks()` recursively walks indirect block levels and stores file block addresses.

`ufs_dump()` is called in frozen kernel dump state:
- Verifies `dump_info` still matches the inode and modification timestamp.
- Verifies the requested write fits in the file.
- Converts file-relative logical blocks to physical disk blocks using `dump_info`.
- Writes contiguous disk block runs directly with `bdev_dump()`.

## ACL and Security Attribute Operations

`ufs_getsecattr()` filters ACL-related masks, enters lockfs only when ACL data is requested, and calls `ufs_acl_get()` under `i_contents`.

`ufs_setsecattr()`:
- Requires a valid ACL/default ACL request.
- Reorders `i_rwlock` acquisition differently for directories and non-directories to match UFS transaction ordering.
- Rejects read-only filesystems and filesystems with `vfs_nosetsec`.
- Wraps ACL updates in `TOP_SETSECATTR`.
- Calls `ufs_acl_set()` under `i_contents`.
- Retries once on logged `ENOSPC` after delete queue draining.
- Reacquires `i_rwlock` as reader for directory callers before returning because the caller expects it held.

## Important Behaviors and Invariants

- Forced unmount is commonly represented by `ip->i_ufsvfs == NULL` and returns `EIO`.
- UFS uses `i_seq` as a vnode attribute sequence number; many metadata-changing operations increment it explicitly.
- Large-file support depends on mount flags and updates `FSLARGEFILES` in the superblock when a file grows past 2GB.
- Fast symlinks store link data in inode block fields starting at `i_db[1]`.
- UFS holes are significant across getpage, putpage, mmap protection, fallocate handling, and dump eligibility.
- Shadow inodes and quota inodes are treated as metadata for logging when dirty pages reach `ufs_putapage()`.
- Delete queue draining is a standard recovery path for logged ENOSPC because pending deletes may hold reclaimable blocks/inodes.
- Lock ordering is central: comments repeatedly document avoiding deadlocks among lockfs, address-space locks, inode locks, quota locks, and locked pages.

## Research Notes

This file is the operational core for illumos UFS vnode behavior. Any modification here can affect filesystem correctness, crash consistency, VM fault behavior, quota accounting, directory atomicity, or lockfs quiesce semantics. The highest-risk areas are `wrip()`, `ufs_getpage()`, `ufs_putapage()`, `ufs_rename()`, `ufs_map()`, and the transaction-wrapped namespace/attribute operations.
