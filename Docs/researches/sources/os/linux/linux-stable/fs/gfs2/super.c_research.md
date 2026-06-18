# File Research: sources/os/linux/linux-stable/fs/gfs2/super.c

## Scope

This file implements GFS2 superblock operations and high-level filesystem lifecycle behavior: journal index cleanup, transition between read-only/read-write operation, statfs accounting and sync, freeze/thaw, inode writeback/dirtying, mount option display, inode eviction/deletion, inode slab allocation, and local statfs inode helpers.

## Public And Internal APIs Covered

- Journal helpers: `gfs2_jindex_free()`, `gfs2_jdesc_find()`, `gfs2_jdesc_check()`.
- RW/RO transitions: `gfs2_make_fs_rw()`, `gfs2_make_fs_ro()`, `gfs2_put_super()`, `gfs2_sync_fs()`.
- Statfs: `gfs2_statfs_change_in()`, `gfs2_statfs_change_out()`, `gfs2_statfs_init()`, `gfs2_statfs_change()`, `update_statfs()`, `gfs2_statfs_sync()`, `gfs2_statfs()`.
- Freeze/thaw: `gfs2_lock_fs_check_clean()`, `gfs2_freeze_func()`, `gfs2_freeze_super()`, `gfs2_freeze_fs()`, `gfs2_thaw_super()`.
- Inode metadata: `gfs2_dinode_out()`, `gfs2_write_inode()`, `gfs2_dirty_inode()`, `gfs2_drop_inode()`, `gfs2_evict_inode()`.
- VFS operation table: `gfs2_super_ops`.
- Local statfs helpers: `free_local_statfs_inodes()`, `find_local_statfs_inode()`.

## Control Flow And Behavior

`gfs2_jindex_free()` detaches the journal descriptor list under `sd_jindex_spin`, clears `sd_jdesc` under `sd_log_flush_lock`, frees each descriptor's journal extents, drops the journal inode, and frees descriptor memory. `gfs2_jdesc_check()` validates journal file size, computes block count, and rejects journals that still need allocation.

`gfs2_make_fs_rw()` invalidates the local journal glock's metadata, rejects unknown local journal sequence state, initializes quotas, and sets `SDF_JOURNAL_LIVE` if successful. `gfs2_make_fs_ro()` stops delete work and GFS2 threads, syncs quotas/statfs, performs two log flushes so revokes can be written before shutdown clears journal liveness, waits for an empty log, and cleans up quotas.

Statfs uses master and local statfs-change inodes. `gfs2_statfs_change()` journals the local statfs buffer, updates local counters under `sd_statfs_spin`, and wakes statfs sync when the configured percentage threshold is exceeded. `gfs2_statfs_sync()` locks the master statfs inode exclusively, reads master counters, starts a transaction, merges local counters into master with `update_statfs()`, zeros local counters, and clears forced sync. `gfs2_statfs_slow()` can instead lock every rgrp asynchronously and sum verified rgrp counters.

Freeze first freezes the VFS superblock, then `gfs2_lock_fs_check_clean()` locks journal glocks shared, unlocks the shared freeze glock, takes the freeze glock exclusively with recovery semantics, and checks every journal head for clean unmount state. Failures thaw and retry, especially when recovery is in progress. Thaw re-acquires shared freeze locking and clears `SDF_FREEZE_INITIATOR` / `SDF_FROZEN`.

`gfs2_dinode_out()` serializes VFS inode state and GFS2 inode fields into an on-disk dinode. `gfs2_dirty_inode()` handles atime-style updates even when called with varied lock/freeze contexts: it acquires the inode glock if needed, starts a dinode transaction if none exists, writes the dinode buffer, then unwinds.

Eviction separates linked inode cleanup from unlinked dinode deletion. `gfs2_drop_inode()` notices remote iopen demote requests and can clear nlink locally; under memory pressure it queues deferred verification/delete work. `evict_should_delete()` verifies that an unlinked dinode is still marked `GFS2_BLKST_UNLINKED`, instantiates the inode glock, and may upgrade the iopen glock. `evict_unlinked_inode()` deallocates exhash directories, xattrs, file blocks, then the dinode. `evict_linked_inode()` flushes dirty metadata/data and truncates page cache. Final eviction always drops reservations, ordered inode state, page cache, dir hash state, and glock references.

## State And Data Structures

Key superblock state includes journal descriptor lists, local/master statfs counters and buffers, freeze glock/holder, journal live/error flags, log flush locks, local statfs inode list, inode/rgrp/glock caches, and mount option structures. Inode eviction uses `i_iopen_gh`, `i_gl`, `i_res`, `i_eattr`, `i_diskflags`, glock flags, and block type state.

## Dependencies

This file ties GFS2 to VFS super operations, writeback controls, freeze/thaw APIs, glock locking, journal/log/revoke machinery, quota subsystem, statfs inode metadata, rgrp verification, directory/file/xattr deallocation, and sysfs teardown.

## Risks And Invariants

Unmount must stop recovery and journal writes before freeing glocks, rgrps, and journal descriptors. Freeze must not report success unless every journal is clean under the exclusive freeze glock. Deleting an unlinked inode must verify bitmap state before reading the dinode block. Memory pressure paths avoid direct DLM calls and use deferred glock put/delete work. Statfs local/master counters can be temporarily approximate but must be merged transactionally. Dirty inode updates must not start transactions after withdrawal or without correct glock state.
