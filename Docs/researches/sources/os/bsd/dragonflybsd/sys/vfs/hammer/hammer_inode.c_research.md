# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_inode.c

## Role

Implements HAMMER in-memory inode caching, vnode association, inode creation/loading, pseudo-filesystem metadata caching, inode dirtying, dependency-aware flush setup, backend inode synchronization, deletion, reclaim throttling, and unmount cleanup.

## Inode Indexes

- `hammer_ino_rb_compare()` orders cached inodes by localization, object id, and as-of TID.
- `hammer_redo_rb_compare()` orders inodes by redo FIFO start.
- Lookup helpers support exact lookup, all-history scanning for one object, and PFS-localization scanning.
- `hammer_pfs_rb_compare()` indexes cached PFS metadata by localization.
- RB generators create inode and PFS trees plus special lookup support for `hammer_inode_info`.

## Vnode Lifecycle

- `hammer_vop_inactive()` recycles zero-link inodes quickly and queues dirty state before reclaim pressure grows.
- `hammer_vop_reclaim()` breaks vnode/inode association under the inode lock, marks reclaim state, clears vnode dirty state, and releases the inode.
- `hammer_get_vnode()` creates or reacquires a vnode for a referenced inode, sets vnode type/ops, device aliases, root flags, and VM object sizing for regular files.
- `hammer_inode_dirty()` marks the vnode dirty when inode mod flags are present.

## Inode Lookup and Creation

- `hammer_get_inode()` first checks the RB cache, then loads the inode record from the B-tree using directory node-cache hints, copies leaf/data into memory, initializes per-inode B-tree caches, and attaches PFS metadata.
- `hammer_get_dummy_inode()` creates a read-only dummy FIFO inode for broken directory entries without marking it as on-disk.
- `hammer_find_inode()` returns only cached, non-dummy inodes.
- `hammer_create_inode()` creates a new in-memory inode, allocates an object id or PFS root id, initializes inode leaf/data, inherits nohistory/nodump flags, assigns uid/gid UUIDs, sets directory capability flags by filesystem version, and inserts the inode into the cache.
- `hammer_free_inode()` releases node caches, reclaim state, object-id cache, PFS refs, and memory.

## Pseudo-Filesystem Handling

- `hammer_load_pseudofs()` loads or creates an in-memory PFS record. PFS records are stored under the real root inode, not the PFS root inode.
- `hammer_save_pseudofs()` replaces an in-memory PFS record by marking any in-memory old record deleted and adding a new general record.
- `hammer_mkroot_pseudofs()` creates a root directory inode for a PFS if absent and increments its link count.
- `hammer_unload_pseudofs()` tries several flush cycles to detach all inodes for a localization, returning `ENOTEMPTY` if users still hold files.
- `hammer_rel_pseudofs()` removes cached PFS metadata once its lock refs drop to zero.

## Dirtying and Timestamp Updates

- `hammer_modify_inode()` sets inode dirty flags, reserves inode space accounting, marks transactions with `HAMMER_TRANSF_NEWINODE` on first dirty transition, and updates vnode dirty state.
- `hammer_update_atime_quick()` can update in-memory atime without the filesystem token when the inode already has pending ATIME state.
- `hammer_update_itimes()` updates on-disk atime/mtime in place. MTIME uses UNDO; ATIME-only updates use no-undo modification because mtime/atime are outside the inode CRC region.

## Flush Group Setup

- `hammer_flush_inode()` assigns dirty inodes to flush groups, creates new groups when necessary, closes overfull groups, and handles IDLE/SETUP/FLUSH states.
- `hammer_setup_parent_inodes()` and `hammer_setup_parent_inodes_helper()` walk directory-entry dependencies upward so a child inode is only flushed when it has valid namespace connectivity.
- Recursion is capped at depth 20 to avoid kernel stack blowout; unresolved dependencies set `CONN_DOWN` and `REFLUSH`.
- `hammer_flush_inode_core()` transitions an inode into `HAMMER_FST_FLUSH`, snapshots frontend inode state into backend `sync_*` fields, moves eligible records into the flush group, handles truncation state, and auto-closes large groups.

## Record Dependency Handling

- `hammer_setup_child_callback()` scans an inode’s in-memory record tree and decides which records can join the current flush group.
- Idle records can flush immediately.
- Setup records represent dependencies, commonly directory adds/deletes tied to target inodes.
- Directory adds can force target inode flushing so the target becomes visible in the same group.
- Overfull groups trigger reflush/resignal to avoid exhausting UNDO space.
- Already flushing directory records can belong to older groups and still count as effectively flushed for the current group.

## Backend Sync

`hammer_sync_inode()` is the core backend flusher path:

- Initializes a cursor using inode data-cache hints.
- Computes the link count that should be synchronized by accounting for directory records in or out of the current flush group.
- Processes pending truncation by deleting on-media data beyond the aligned truncation point.
- Emits REDO termination for truncations when version 4+ redo state exists.
- Syncs in-memory records through `hammer_sync_record_callback()`.
- Re-seeks toward the cached inode node when possible before updating inode metadata.
- Deletes auxiliary records and marks the inode deleted when link count is zero, records are gone, and deletion is pending.
- Writes initial or replacement inode records through `hammer_update_inode()`.
- Uses `hammer_update_itimes()` for timestamp-only updates when possible.
- Reports critical errors through `hammer_critical_error()`.

## Record Sync Details

- `hammer_sync_record_callback()` processes only records in the inode’s current flush group.
- It sets backend interlock flags so frontend deletion state cannot change unsafely.
- Frontend-deleted directory adds are converted into delete-on-disk records when needed.
- New records receive the transaction TID and create timestamp.
- REDO data records generate `HAMMER_REDO_TERM_WRITE` when committed.
- `EDEADLK` restarts cursor state.
- High metadata pressure or severe VM paging temporarily unlocks the cursor, finalizes the flusher, and relocks the cursor.

## Completion, Deletion, and Reclaim

- `hammer_sync_inode_done()` merges backend `sync_flags` back to frontend state, handles `WOULDBLOCK`, removes completed inodes from flush groups, wakes waiters, schedules reflushes, clears reservations, and releases clean idle inodes.
- `hammer_wait_inode()` waits for FLUSH or signaled SETUP state and forces async flushing if the group is not yet closed.
- `hammer_inode_unloadable_check()` marks zero-link, non-read-only inodes as deleting and truncates buffers to zero.
- `hammer_test_inode()` triggers pending reflush after dependency resolution.
- `hammer_destroy_inode_callback()` forcibly tears down in-memory records and flush state during critical-error unmount cleanup.
- `hammer_reload_inode()` updates cached inode read-only flags when mount state changes.

## Reclaim Throttling

- `hammer_inode_wakereclaims()` clears reclaim accounting and wakes blocked reclaim waiters.
- `hammer_inode_waitreclaims()` throttles inode creation/loading when too many detached dirty inodes accumulate, using per-process pressure history.
- `hammer_inode_inostats()` maintains a small loose set-associative per-pid statistic with decay over ticks.
- Disabled `hammer_inode_waithard()` shows an older harder flush-wait recovery mechanism.

## Research Notes

This file is the main bridge between HAMMER’s VFS-facing inode/vnode model and its copy-on-write historical B-tree storage. The most important behavior is dependency-aware flushing: directory entries, target inodes, link counts, truncations, REDO/UNDO state, and inode records are all synchronized as a group without violating visibility or crash-recovery invariants.
