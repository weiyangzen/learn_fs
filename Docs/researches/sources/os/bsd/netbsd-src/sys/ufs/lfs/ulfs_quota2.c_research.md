# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.c

Read completely: 1636 lines.

Implements quota2 support for ULFS/LFS. Quota2 stores quota metadata in special quota inodes referenced by the LFS superblock, with a header, default entry, free list, and hash chains of quota entries.

On-disk access:
- `getq2h()` reads and validates quota file block 0 as `struct quota2_header`.
- `getq2e()` reads a quota entry at logical block/offset and validates alignment and non-short read.
- `quota2_walk_list()` walks a linked list of entries, using callbacks for lookup/delete/cursor enumeration and writing modified buffers when callbacks change parent pointers.
- `quota2_q2ealloc()` allocates a quota entry from the free list, grows the quota file by a block if needed, initializes new entries with `lfsquota2_addfreeq2e()`, copies default limits, sets id, and inserts into the appropriate hash bucket.

Accounting:
- `getinoquota2()` attaches inode dquots, locks all relevant dquots, allocates on-disk entries when needed, and returns locked quota-entry buffers.
- `quota2_check()` implements both block and file accounting. Negative changes subtract usage; positive changes check hard/soft/grace status with `lfsquota_check_limit()`, issue warnings, set grace-expiration time on soft-limit crossing, and writes usage updates if allowed.
- `lfs_chkdq2()` and `lfs_chkiq2()` dispatch block and file accounting to `quota2_check()`.

Quotactl handlers:
- `lfsquota2_handle_cmd_get()` returns default or per-id quota values.
- `lfsquota2_handle_cmd_put()` updates default limits or allocates/updates a per-id entry.
- `lfsquota2_handle_cmd_del()` resets one object type from defaults and frees the quota entry entirely if both object types now match defaults and usage is zero.
- `quota2_fetch_q2e()` and `quota2_fetch_quotaval()` read per-id entries through dquot lookup.

Cursor support:
- Defines `struct ulfsq2_cursor`, stored inside the public `quotakcursor` scratch area.
- `lfsquota2_handle_cmd_cursoropen/close/rewind/atend/cursorskipidtype()` manage cursor lifecycle and filtering.
- `lfsquota2_handle_cmd_cursorget()` performs two passes: first scans hash chains under `lfs_dqlock` to produce keys, then fetches values by dquot lookup without holding the list lock.
- Cursor state tracks defaults, user/group completion, hash position, uid position inside a bucket, and whether the block half of an odd key/value pair was already returned.

Mount/unmount:
- `lfs_quota2_mount()` checks `lfs_use_quota2`, validates `lfs_quota_magic`, verifies configured user/group quota inode numbers, `VFS_VGET()`s quota inodes, stores quota vnodes/credentials, increments writecount, marks group quota vnode system, and sets `MNT_QUOTA`.
- `lfsquota2_umount()` closes active quota vnodes and clears mount quota pointers.

Synchronization:
- `lfs_q2sync()` and `lfs_dq2sync()` are stubs; quota2 writes metadata buffers directly rather than using dirty dquot writeback.

Risks and notes:
- The locking contract is explicit: entry data require the associated dquot interlock, while header/list pointers require global `lfs_dqlock`.
- Several corruption cases panic, including invalid header magic/type, truncated quota files, and misaligned entries.
- Cursor iteration returns `EDEADLK` if hash size changes or an entry disappears between key and value passes, forcing callers to restart.
- `lfs_quota2_mount()` stores `l->l_cred` without an explicit credential hold in this file.
- User quota vnode writecount is incremented but only the group quota vnode visibly gets `VV_SYSTEM` set in this implementation.
