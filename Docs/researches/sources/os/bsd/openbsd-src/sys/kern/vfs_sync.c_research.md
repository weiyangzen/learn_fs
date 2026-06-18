# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_sync.c

Read completely: 371 lines.

Implements the filesystem syncer daemon and synthetic syncer vnodes used to lazily flush dirty vnodes and periodically call filesystem sync operations.

Syncer queue model:
- `SYNCER_MAXDELAY` and `syncdelay` define a ring of delayed work queues.
- `vn_initialize_syncerd()` allocates the hash/ring of pending sync lists and records the mask.
- `vn_syncer_add_to_worklist()` inserts or moves a vnode into a future slot, clamping delay and marking `VBIOONSYNCLIST`.
- Dirty vnodes are scheduled by `reassignbuf()` in `vfs_subr.c`.

Daemon loop:
- `syncer_thread()` advances one slot per second.
- For each vnode in the current slot, it tries `vget(... LK_NOWAIT)`.
- If locking fails, the vnode is rescheduled one second later.
- If locking succeeds, the daemon calls `VOP_FSYNC(... MNT_LAZY ...)`, releases the vnode, and reschedules if it remains at the head of the same list.
- Diagnostic builds panic if a non-block vnode with no dirty buffers remains stuck on the worklist after fsync.
- The loop yields between items and sleeps only for the remainder of the one-second period.

Syncer vnode:
- `sync_vops` defines a minimal vnode operation vector for syncer vnodes, with `sync_fsync()`, `sync_inactive()`, and `sync_print()`.
- `vfs_allocate_syncvnode()` creates one syncer vnode per mount, marks it with a writecount, scatters initial sync delays across the ring, and records it in `mp->mnt_syncer`.
- `sync_fsync()` only acts on `MNT_LAZY`: it reschedules itself, temporarily clears `MNT_ASYNC`, and calls `VFS_SYNC(mp, MNT_LAZY, ...)` while the mount is busy.
- `sync_inactive()` removes a decommissioned syncer vnode from the worklist, clears mount linkage, resets writecount, and drops the vnode.
- `sync_print()` provides debug labeling.

Risks and notes:
- Worklist membership is protected at `splbio()` and represented by `VBIOONSYNCLIST`; duplicate insertion/removal must stay consistent.
- The syncer deliberately uses nonblocking vnode locks and reschedules failures, so heavily contended vnodes may be delayed.
- Syncer vnodes carry `v_writecount = 1`, making inactive handling nonstandard.
- `sync_fsync()` temporarily overrides `MNT_ASYNC` to make lazy filesystem sync behavior meaningful.
- The daemon is pacing-oriented, not a hard real-time writeback guarantee.
