# File Research: sources/os/linux/linux-stable/fs/gfs2/incore.h

## Scope

This header defines the central in-memory structures and flags for GFS2: log operations, resource groups, buffers, lock names, glock operations/state, holders, quota data, reservations, inodes, transactions, journals, mount arguments, lock manager state, per-cpu lock stats, and the superblock-private `gfs2_sbd`.

## Key Structures

- `gfs2_log_header_host` and `gfs2_log_operations` describe journal headers and log element callbacks.
- `gfs2_bitmap` and `gfs2_rgrpd` represent resource-group bitmaps, clone bitmaps, allocation state, reservation tree, and rgrp glock linkage.
- `gfs2_bufdata` links buffer_heads to transactions and AIL lists.
- `lm_lockname` is the rhashtable key for glocks, consisting of block/lock number, superblock, and type.
- `gfs2_glock_operations` defines per-type sync, xmote bottom-half, invalidate, instantiate, held, dump, and remote callback hooks.
- `gfs2_holder` represents a queued or granted lock request.
- `gfs2_glock` stores all lock state, flags, holder queue, glops pointer, DLM LVB, object pointer, AIL counters, delayed work, iopen delete fields, and hash/RCU links.
- `gfs2_inode` embeds the VFS inode and adds dinode identity, glocks, quota data, rgrp reservation, allocation goal, size hint, ordered-data list, dir hash cache, disk flags, tree height, dir depth, entry count, and readahead.
- `gfs2_file` stores per-open flock state.
- `gfs2_quota_data`, `gfs2_qadata`, and quota constants represent quota locking/accounting state.
- `gfs2_trans` records transaction reservations, touched buffers, databuffers, revokes, and AIL lists.
- `gfs2_jdesc` tracks journal extents, recovery work, replay counts, and revoke replay state.
- `gfs2_args` and `gfs2_tune` hold mount options and tunables.
- `lm_lockstruct` tracks lockspace identity, DLM handles, recovery flags/generations, lockspace semaphores, and callback synchronization.
- `gfs2_sbd` is the filesystem-wide state object: VFS superblock, lock stats, flags, computed geometry, mount args, lock glocks, inode roots, statfs state, rgrp tree, journal index, workqueues, daemons, quota state, log/AIL state, freeze state, filesystem names, and debugfs directory.

## Important Flags And Inline Helpers

- `DIO_WAIT` and `DIO_METADATA` describe invalidate/sync behavior.
- `BH_Pinned` and `BH_Escaped` extend buffer state for journal handling.
- `DFL_*` flags describe DLM recovery state.
- `GLF_*` flags cover glock lock in progress, demotion, dirty state, frozen replies, LRU membership, instantiate state, iopen delete work, cancellation, and deferred delete.
- `GIF_*` flags cover inode quota lock, mmap shared-write page state, and pending glop.
- `SDF_*` flags cover journal, withdrawal, recovery, DLM unlock skipping, AIL flush, freeze, kill, eviction, and frozen state.
- Helpers include `GFS2_I()`, `GFS2_SB()`, `glock_sbd()`, `gfs2_aspace()`, lock-stat increments, `gfs2_max_stuffed_size()`, and glock number/type accessors.

## Dependencies

- This header is the shared state contract for nearly all GFS2 implementation files.
- It depends on Linux VFS, kobject, workqueue, DLM, buffer_head, RCU, rbtrees, percpu, lockref, rhashtable, mutex, and on-disk GFS2 structures.

## Risks And Invariants

- Structure fields are shared across many subsystems; locking discipline is external and must match comments and users.
- Clone bitmap comments define an allocation invariant: blocks freed in a transaction cannot be reallocated in that same transaction.
- `lm_lockname` must avoid interior padding because it is used as an rhashtable key.
- `gfs2_inode` embeds `struct inode` first, making `GFS2_I()` effectively a container cast relied on throughout the code.
- `gfs2_sbd` combines log, DLM, rgrp, quota, freeze, and debug state; partial initialization or teardown ordering mistakes can affect multiple subsystems.
