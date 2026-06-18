# File Research: sources/os/linux/linux/fs/gfs2/quota.c

Implements GFS2 clustered quota accounting. It maintains per-ID quota data objects, local per-node quota-change slots, quota LVB caching, periodic syncing into the global quota file, allocation checks, and VFS quotactl operations.

Important behavior:
- Quota changes are accumulated in node-local `quota_changeN` files and periodically synced to the shared quota file to reduce cluster contention.
- Quota data objects are hashed by superblock and `kqid`, protected by bucket locks and RCU, reference-counted with `lockref`, and reclaimable through `gfs2_qd_lru` and a shrinker.
- `slot_get`/`slot_put()` allocate local quota-change slots from `sd_quota_bitmap`; `bh_get`/`bh_put()` attach quota data to the correct quota-change buffer and slot.
- `gfs2_quota_hold()` collects current uid/gid plus optional ownership-change uid/gid quota data for an inode.
- `gfs2_quota_lock()` sorts quota data to avoid deadlocks, locks quota glocks, and refreshes LVBs from disk when stale or forced.
- `do_qc()` updates a local quota-change slot inside the current transaction and manages `QDF_CHANGE`, slot refs, and quiet warning state.
- `gfs2_quota_check()` enforces hard limits and soft-warning reporting unless quotas are off/account-only or the caller bypasses checks.
- `gfs2_quota_change()` records allocation/free deltas for matching user/group quota data.
- `do_sync()` locks all selected quota glocks plus the quota inode, reserves allocation/transaction space, applies local deltas into the shared quota file, subtracts them from local change slots, and flushes the log.
- `gfs2_quota_sync()` iterates dirty quota data in batches, advances `sd_quota_sync_gen`, and uses `do_sync()`.
- `gfs2_quota_init()` scans the node-local quota-change file at mount, reconstructs in-core dirty quota data and slot bitmap state, and repairs duplicate identifiers by zeroing duplicate slots.
- `gfs2_quota_cleanup()` disposes unused quota data and frees the slot bitmap after journal shutdown/no-recovery conditions.
- `gfs2_quotad()` periodically syncs statfs and quota data, wakes on forced statfs sync, and reports errors into the log subsystem.
- `gfs2_quotactl_ops` implements state query, get quota, set quota, and quota sync.

The main correctness risks are lock ordering across quota glocks and inode glocks, syncing local changes without losing deltas, quota-change slot lifetime, stale LVB refresh, and interaction with journal flush/withdraw paths.
