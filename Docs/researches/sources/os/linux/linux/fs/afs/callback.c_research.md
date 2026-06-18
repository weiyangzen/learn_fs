# File Research: sources/os/linux/linux/fs/afs/callback.c

Purpose: handles callback invalidation from AFS fileservers, including vnode callbacks, volume-level callbacks, mmap invalidation, and callback-state reinitialization.

Key interfaces:
- `afs_invalidate_mmap_work()`.
- `afs_init_callback_state()`.
- `afs_break_callback()` / `__afs_break_callback()`.
- `afs_break_callbacks()`.

Implementation notes:
- Mmap invalidation unmaps all pages for the vnode mapping so later faults revalidate.
- Server callback-state reinitialization clears callback promises for all volumes attached to the server and queues mmap invalidation when needed.
- Breaking a vnode callback clears new-content state, clears permits, increments callback break counters, updates volume break check, wakes lock waiters, and queues mmap invalidation for mapped files.
- Volume callback break clears per-server and volume callback expiries, increments `cb_v_break`, releases RCU before walking open mmap list, and initializes callbacks for open mmaps.
- Callback batches are grouped by volume ID; volume-wide breaks use vnode/unique zero.

Dependencies:
- Uses volume and server lists, seqlocks, RCU, inode lookup by FID, open mmap lists, and permit/cache callback tracking.

Edge cases:
- If a matching volume or inode is absent, callback break is traced as a miss rather than fatal.
- `afs_break_volume_callback()` assumes a valid volume pointer after lookup; caller path must ensure this is safe for volume-wide callback records.
