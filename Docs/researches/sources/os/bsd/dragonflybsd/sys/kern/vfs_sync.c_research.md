# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_sync.c

## Role

This file implements DragonFly BSD's per-filesystem syncer infrastructure. It schedules delayed vnode writeback, owns the syncer kernel thread state per mount, implements dirty-vnode flag transitions, and creates the synthetic syncer vnode that periodically drives `vfs_msync()` and `VFS_SYNC()`.

## Main Responsibilities

- Defines delayed writeback sysctls and tunables:
  - `kern.syncdelay`
  - `kern.filedelay`
  - `kern.dirdelay`
  - `kern.metadelay`
  - `kern.retrydelay`
  - `debug.rush_requests`
- Maintains a `SYNCER_MAXDELAY` time wheel of `struct synclist` buckets in `struct syncer_ctx`.
- Exposes syncer worklist operations:
  - `vn_syncer_add()`
  - `vn_syncer_remove()`
  - `vn_syncer_count()`
- Tracks vnode dirty flags:
  - `vsetisdirty()` and `vclrisdirty()` for dirty inode state.
  - `vsetobjdirty()` and `vclrobjdirty()` for dirty VM object state.
- Creates and stops per-mount syncer threads with `vn_syncer_thr_create()` and `vn_syncer_thr_stop()`.
- Implements `syncer_thread()`, which wakes once per second or on triggers/rush jobs, processes expired vnodes, and invokes `VOP_FSYNC()` with lazy or nowait semantics.
- Provides manual acceleration and triggering:
  - `vn_syncer_one()`
  - `speedup_syncer()`
  - `trigger_syncer_start()`
  - `trigger_syncer_stop()`
  - `trigger_syncer()`
- Implements the syncer vnode VOPs and allocation path:
  - `vfs_allocate_syncvnode()`
  - `sync_fsync()`
  - `sync_inactive()`
  - `sync_reclaim()`
  - `sync_print()`
- Implements `vsyncscan()`, a syncer-list-only vnode scan for filesystems that maintain dirty vnodes on the syncer list and set `MNTK_THR_SYNC`.

## Synchronization and Lifetime Model

- Each mount's `syncer_ctx` owns `sc_token`; it protects `v_synclist`, `VONWORKLST`, the time wheel, and syncer counters.
- `vn_syncer_add()` intentionally depends on the syncer token and must not block in ways that would deadlock callers already in syncer context.
- `vn_syncer_remove()` may reacquire the syncer token, then rechecks dirty flags and dirty-buffer trees before removal.
- `vn_syncer_thr_stop()` sets `SC_FLAG_EXIT`, wakes the thread, and waits for `SC_FLAG_DONE` before destroying the work queue and context.
- `sync_reclaim()` removes the syncer vnode from the worklist during vnode reclamation, asserting that `mp->mnt_syncer` no longer points to it.

## Notable Design Details

- Dirty vnodes are scheduled into a ring bucket based on requested delay; negative delay is used by scan paths to reposition a vnode at an explicit slot.
- File, directory, and metadata delay classes are selected elsewhere, especially by `reassignbuf()` in `vfs_subr.c`.
- `syncer_thread()` moves each vnode to `retrydelay` before attempting fsync. If fsync cannot get the vnode lock in non-forced mode, the vnode remains scheduled for retry.
- A special syncer vnode is itself scheduled on the worklist; its lazy fsync drives full mount-level work through `vfs_msync()` and `VFS_SYNC()`.
- `speedup_syncer()` advances processing under memory pressure or dependency pressure by increasing the global `rushjob` sequence and waking a mount's syncer context.
- `vsyncscan()` scans only syncer-list vnodes rather than the full mount vnode list, which is critical for mounts with very large vnode populations.

## Cross-File Relationships

- `vfs_subr.c` calls `vn_syncer_add()`, `vn_syncer_remove()`, `vclrobjdirty()`, and `vsyncscan()` while moving buffers and cleaning VM pages.
- `vfs_syscalls.c` allocates a syncer vnode during successful mount and decommissions it during unmount.
- `vfs_vfsops.c` stops syncer threads after a successful filesystem unmount wrapper call.
- Filesystem implementations interact through vnode dirty flags, `VOP_FSYNC()`, and mount flags such as `MNTK_THR_SYNC`, `MNTK_NOMSYNC`, and `MNT_RDONLY`.

## Research Notes

- The syncer is a central delayed-write policy component. It intentionally trades immediate persistence for batching, retry, and reduced churn from short-lived files.
- The most important correctness invariants are `VONWORKLST` membership consistency, token discipline around the time wheel, syncer vnode teardown during unmount, and avoiding full vnode-list scans on filesystems that opt into threaded sync.
