# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_lockfs.c

## Purpose

`ufs_lockfs.c` implements UFS filesystem locking, quiescing, flushing, thawing, and reconciliation. It backs the `lockfs` ioctl interface and the internal lockfs begin/end protocol used by UFS vnode operations to cooperate with filesystem suspension, backup locks, hard locks, error locks, and getpage faults.

The file is a state-machine layer over the mount's `ulockfs` structure. It tracks active vnode operations, fallocate-style operations, recursive VOP calls through thread-specific data, pending quiesce requests, and lock compatibility masks.

## Main Interfaces

Lock state and ioctl operations:

- `ufs_fiolfs()` and `ufs__fiolfs()` apply a new lockfs state.
- `ufs_fiolfss()` reports current lockfs state.
- `ufs_getlfd()` validates lock requests and lock keys.
- `ufs_freeze()` installs a new requested lock state in `ulockfs`.
- `ufs_quiesce()` sets softlock state and waits for active operations to drain.
- `ufs_thaw()` performs lock-type-specific cleanup and wakes blocked threads.

Flush and reconciliation:

- `ufs_flush_inode()` pushes and invalidates one inode.
- `ufs_flush()` flushes dnlc, delete/idle queues, quotas, inodes, superblock, block-device pages, buffers, and log transactions.
- `ufs_reconcile_fs()` reloads safe superblock fields from disk.
- `ufs_reconcile_inode()` reloads safe inode fields from disk.
- `ufs_reconcile()` coordinates flush, superblock reconciliation, inode reconciliation, and a second flush.

VOP protocol:

- `ufs_lockfs_begin()` starts normal lockfs protocol for a VOP.
- `ufs_lockfs_trybegin()` is the non-blocking variant.
- `ufs_lockfs_begin_getpage()` is the getpage/page-fault-specific variant.
- `ufs_lockfs_end()` terminates protocol and decrements active counters.
- `ufs_check_lockfs()` blocks or rejects operations based on the current lock mask.
- `ufs_lockfs_tsd_destructor()` frees per-thread recursion records.

## Quiesce And Flush

`ufs_quiesce()` obtains the current thread's lockfs TSD record, increments `lwp_nostop` to avoid `/proc` stop deadlocks while a softlock is pending, sets `SLOCK`, and waits until `ul_vnops_cnt` and `ul_falloc_cnt` drain. Fallocate threads have special handling so one fallocate flow can proceed once other VOPs drain and no fallocate write lock is already held.

`ufs_flush()` purges DNLC entries for the filesystem, drains delete and idle queues, syncs quota records, scans inodes with `ufs_flush_inode()`, writes superblock/summary state when dirty, invalidates block-device pages and buffers, drains queues again, checks clean state, and if logging is active commits and rolls the log unless `LDL_NOROLL` prevents it.

`ufs_thaw()` adjusts behavior for write, hard, and error locks. For write locks it flushes twice, blocks access-time/deletion side effects, invalidates buffers, and checks no mlocked pages remain. For hard/error locks it forcibly invalidates inode pages and buffers. When unlocking from `NOIDEL`, it flushes deleted files before restoring normal access/deletion/superblock behavior.

## Applying Lockfs State

`ufs__fiolfs()` validates the requested lock, guards against unmounted filesystems, prevents write/error locks when accounting or swap files are active, suspends reclaim and delete threads, increments `ufs_quiesce_pend`, rejects incompatible current states, validates lock keys, saves the prior state, freezes the new state, marks lockfs busy, and quiesces active VOPs.

It handles error-lock transitions specially. Setting an error lock marks the filesystem bad and disables delayed I/O; unlocking or relocking error locks passes state into reconciliation and fix-on-panic cleanup. A user-applied error lock can call `ufs_fault()` unless on-error panic handling is configured.

After quiescing, it reconciles if the filesystem had been write-locked or error-locked, flushes dirty state, thaws to the new state, clears modified/busy flags, frees old comments, wakes pollers, resumes delete/reclaim threads, and returns. On failure it restores the old lock state unless hard-locked and avoids `ufs_thaw()` after signal interruption during quiesce because that path can deadlock with getpage.

## Reconciliation

`ufs_reconcile_fs()` reads the on-disk superblock and verifies structural fields that must not change: block layout, sizes, shifts, geometry, postbl format, and magic. It refuses unsafe states for error-lock unlocks, reloads summary info, updates allowed mutable fields, restarts reclaim when needed, and lets on-disk bad/clean/error state override in-memory state under defined conditions.

`ufs_reconcile_inode()` rejects in-core inodes that still have dirty flags after quiesce/flush. It reads the on-disk dinode, verifies immutable identity fields such as mode, generation, UID, and GID, then refreshes allowed mutable fields: size, flags, blocks, link count, and direct/indirect block pointers.

`ufs_reconcile()` first flushes as much in-memory state as possible, reconciles superblock and all relevant inodes, then flushes again to discard potentially stale allocation data.

## VOP Begin/End Protocol

`ufs_lockfs_begin()` detects recursive VOPs using a thread-specific list of `ulockfs_info_t` records and bypasses lock accounting for recursive calls or raw internal lockfs paths. For top-level VOPs it increments either `ul_vnops_cnt` or `ul_falloc_cnt`, checks current lock state and global `ufs_quiesce_pend`, may block in `ufs_check_lockfs()`, records the active filesystem in TSD, and sets `T_DONTBLOCK`.

`ufs_lockfs_end()` invalidates the TSD record, clears `T_DONTBLOCK` when returning from the top-level VOP, decrements the fallocate or normal VOP counter, clears fallocate state when needed, and broadcasts when counters reach zero.

`ufs_lockfs_trybegin()` mirrors begin logic but returns `EAGAIN` instead of blocking when the current lock conflicts with the requested operation. `ufs_lockfs_begin_getpage()` selects a read or write lock mask based on mapping type and access; it may strip `PROT_WRITE` from read faults so later write faults block correctly under write locks.

`ufs_check_lockfs()` waits while the current `ul_fs_lock` conflicts with the requested mask, respecting `T_DONTPEND`, `T_WOULDBLOCK`, hard/error-lock EIO behavior, interruptibility, and `vfs_dontblock`.

## Invariants And Dependencies

Key invariants:

- Lockfs quiesce must stop new conflicting VOPs and wait for active counters to drain.
- Recursive VOPs on the same filesystem must not self-deadlock through lockfs accounting.
- Hard/error locks can force page and buffer invalidation; write locks require clean, unmapped state.
- Reconciliation only accepts on-disk changes to an explicit set of mutable fields.
- Delete and reclaim threads are suspended outside the lockfs mutex/protocol.
- `ufs_quiesce_pend` is used as a global signal to prevent livelock while a quiesce request is trying to drain VOPs.

Dependencies include UFS vnode operation wrappers, transaction/logmap APIs, inode scanner, quota sync, DNLC purge, delete/idle/reclaim threads, fix-on-panic helpers, VM page invalidation, block-device buffer cache flushing, accounting/swap checks, poll notification, and thread-specific data.

## Research Notes

This is one of the highest-complexity UFS coordination files. Audit attention should focus on counter balance in begin/end error paths, recursive VOP TSD reuse, quiesce interruption handling, fallocate-specific state, reconciliation trust boundaries, and lock transitions involving error or hard locks.
