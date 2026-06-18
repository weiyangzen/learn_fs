# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota_ufs.c

This file implements runtime UFS quota enforcement for blocks and inodes. Its public entry points are `getinoquota`, `chkdq`, `chkiq`, and `dqrele`.

`getinoquota` chooses the `dquot` used by an inode. It requires `vfs_dqrwlock` and the inode contents write lock, ignores disabled quotas, the quota file itself, shadow inodes, and extended attribute directory inodes, and returns `NULL` when the user's quota record has no block or file limits. Otherwise it returns a held dquot whose UID matches the inode owner.

`chkdq` applies block usage deltas to `ip->i_dquot`. Negative changes always succeed, decrement current blocks with underflow protection, clear block warning state, and reset block grace time when usage drops below the soft limit. Positive changes reserve blocks unless the file is owned by uid 0, checking hard limits, soft limits, grace expiration, and the `force` override. It records quota modifications with `DQ_MOD`/`TRANS_QUOTA`, caps forced 32-bit block count overflow at `0xffffffff`, and can either return a user-facing warning string to the caller or log the quota warning directly.

The debug block in `chkdq` is an important consistency check: it recomputes the expected dquot through `getinoquota` or `getdiskquota`, permits only known transient quota errors, and asserts that the inode's cached dquot pointer matches the quota subsystem's view. This is specifically guarded for shadow inodes and extended attribute directories, which must not have quota records.

`chkiq` enforces per-user inode quotas. It requires the quota rwlock as reader, accepts only `+1` or `-1`, and handles two paths: freeing a specific inode through that inode's cached dquot, or allocating/freeing by UID via `getdiskquota`. Allocation checks hard limits, soft limits, file grace time, and `force`; deallocation clears warning state and grace time when usage falls below the soft limit. Shadow inodes and extended attribute directory inodes do not count as user inode allocation.

`dqrele` is the dquot release helper. It locks the dquot, pushes modified quota state with `dqupdate` when the last reference is being released, then drops the reference with `dqput`.

Integration notes: callers must hold the documented inode and quota locks before invoking these routines. Allocation callers rely on quota rollback with negative deltas when subsequent physical allocation fails. The warning-string path allocates kernel memory with `KM_NOSLEEP`, so callers that request messages must free the returned buffer after `uprintf`.
