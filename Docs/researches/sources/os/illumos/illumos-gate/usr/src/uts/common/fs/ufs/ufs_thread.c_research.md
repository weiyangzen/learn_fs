# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_thread.c

## Overview
`ufs_thread.c` implements reusable UFS queue/thread control plus the background workers that reclaim deleted inodes, shrink idle inode caches, scan for deleted inodes left by prior logging mounts, and hard-lock filesystems whose logs have errored.

## Main Responsibilities
- Provide generic `ufs_q` lifecycle helpers: init, start, exit, suspend, continue, and run.
- Process delayed inode deletion through `ufs_delete()`, `ufs_thread_delete()`, and drain helpers.
- Track unreclaimed delete-queue resources for `statvfs`.
- Maintain global idle inode queues and reclaim idle inodes under memory pressure or high-water conditions.
- Scan filesystems for deleted-but-not-reclaimed inodes with `ufs_thread_reclaim()`.
- Run the global hlock worker through `ufs_thread_hlock()`.
- Purge extended attribute directory contents during inode deletion.

## Generic Queue Protocol
- `ufs_thread_init()` initializes mutex, condition variable, low/high water marks, and thread pointer.
- `ufs_thread_start()` creates a kernel thread at `minclsyspri` if one is not already running.
- `ufs_thread_exit()` sets `UQ_EXIT`, wakes the worker, and joins by saved `t_did`.
- `ufs_thread_suspend()` requests `UQ_SUSPEND` and waits for `UQ_SUSPENDED`.
- `ufs_thread_run()` centralizes worker sleep, suspend, exit, and low-water processing behavior with CPR callbacks.

## Delete Queue Behavior
- `ufs_delete()` frees resources of an idle deleted inode: handles lockfs restrictions, removes extended attributes, truncates data, frees the inode, releases quota state, recycles the vnode, and closes the transaction.
- `ufs_thread_delete()` removes one inode at a time from the per-filesystem delete queue to keep suspend latency low.
- `ufs_delete_drain()` can remove a fixed count, all current entries, or continue until empty.
- `ufs_delete_drain_wait()` drains the queue and synchronizes with the delete thread to satisfy POSIX space-availability semantics after unlink/close.
- `ufs_delete_adjust_stats()` adds queued-but-unreclaimed blocks/files into `statvfs` free counts.

## Idle Inode Reclaim
- The idle subsystem splits idle inodes into hashed “junk” and “useful” queues.
- `ufs_thread_idle()` wakes when the global idle queue exceeds the low-water mark and frees roughly half.
- `ufs_inode_cache_reclaim()` wakes the idle thread when memory pressure occurs and the queue is above halfway.
- `ufs_idle_some()` selects idle inodes round-robin, holds them, removes them from idle state, and calls `ufs_idle_free()`.
- `ufs_idle_free()` flushes/invalidate pages, blocks iget through the inode hash lock, removes the inode from cache, releases quota/shadow state, and returns it to the inode cache.
- `ufs_idle_drain()` drains idle inodes for one vfs or all vfs instances.

## Reclaim and Hlock Workers
- `ufs_thread_reclaim()` scans on-disk dinodes, finds deleted inodes with nonzero mode, igets them, and releases them so normal inactive/delete processing reclaims space.
- On successful reclaim scan, it clears `FS_RECLAIMING` and writes the superblock.
- `ufs_thread_hlock()` waits on `ufs_hlock`, then repeatedly calls `ufs_trans_hlock()` until no retry is needed.
- `ufs_attr_purge()` walks an attribute directory, removes entries from DNLC, decrements link counts, and participates in remove transactions.

## Locking and Transactions
- Delete and reclaim paths coordinate with `lockfs`, `vfs_dqrwlock`, `i_contents`, `i_rwlock`, and quota locks.
- `T_DONTBLOCK` prevents recursive blocking in lockfs/transaction-sensitive contexts.
- Transaction macros wrap truncation, inode free, attribute removal, and commit synchronization.
- Idle freeing carefully uses vnode and inode hash locks to prevent new references while reclaiming.

## Research Notes
This file is the main asynchronous maintenance engine for UFS. The highest-risk areas are queue suspend/exit semantics during unmount, vnode reference invariants in idle reclaim, delayed-delete accounting, and transaction boundaries around inode deletion.
