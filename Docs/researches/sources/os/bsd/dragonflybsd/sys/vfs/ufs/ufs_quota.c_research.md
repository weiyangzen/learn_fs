# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_quota.c

## Purpose

Implements UFS quota accounting, enforcement, quotactl operations, and in-core dquot cache management.

## Main Accounting Functions

- `ufs_getinoquota()`: attaches user and group dquot structures to an inode when quotas are enabled.
- `ufs_chkdq()`: applies block usage changes, enforcing hard limits and soft-limit grace periods unless forced.
- `ufs_chkiq()`: applies inode usage changes with analogous hard/soft limit enforcement.
- `ufs_chkdqchg()` and `ufs_chkiqchg()`: validate prospective block/inode increases and emit user warnings.
- `ufs_quotawarn()`: rate-limited warning when quota operations target the quota file itself.
- Diagnostic `ufs_chkdquot()`: asserts modified inodes have dquots when quotas are active.

## Quotactl Functions

- `ufs_quotaon()`: opens a quota file, marks it system, initializes quota grace times from id 0, and scans active writable vnodes to attach dquots.
- `ufs_quotaoff()`: detaches dquots from vnodes, flushes cached dquots for the quota vnode, closes the quota file, and clears mount quota state.
- `ufs_getquota()`: copies a quota record out to user space.
- `ufs_setquota()`: replaces quota limits while preserving current usage and maintaining grace timers.
- `ufs_setuse()`: sets current block/inode usage and resets soft-limit timers where needed.
- `ufs_qsync()`: scans vnodes and syncs modified dquots.

## Dquot Cache Functions

- `ufs_dqinit()`: initializes hash table and free list.
- `ufs_dqget()`: finds or allocates a dquot, reads its record from the quota file, initializes timers/fake state, and returns a referenced structure.
- `ufs_dqrele()`: drops a reference, syncing modified dquots when the last reference is released.
- `ufs_dqsync()`: writes a modified quota record back to the quota file with dquot locking.
- `ufs_dqflush()`: removes all cached dquots associated with a quota vnode.

## Important Behavior

Block and inode usage decreases never fail and clear warning flags when usage falls. Increases are checked first for all active quotas, then applied. Soft limits are allowed until their grace time expires; hard limits fail immediately.

Quota files are protected from recursive quota accounting by warning and skipping normal charge changes when the quota vnode itself is involved.

## Dependencies And Integration Points

Called from vnode operations, inode lifecycle, allocation/free paths, and `ufs_quotactl()` in `ufs_vfsops.c`. Uses `vmntvnodescan()`, `VOP_READ()`, `VOP_WRITE()`, vnode locking, credentials saved in `ufsmount`, and quota fields embedded in `struct inode`.

## Notes For Future Work

- The dquot cache is global, keyed by quota vnode and id.
- `DQ_LOCK`/`DQ_WANT` provide sleep-based serialization around quota file I/O.
- `ufs_quotaon_scan()` only attaches dquots to vnodes with `v_writecount != 0`.
