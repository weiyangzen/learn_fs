# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_quota.c

## Purpose
Implements UFS disk quotas: quota attachment to inodes, block/inode limit enforcement, quotactl operations, quota vnode management, dquot cache management, soft updates integration, and 32-bit/64-bit quota record conversion.

## Key entry points
- `getinoquota()` attaches user and group dquots to an inode, skipping system vnodes and negative UID/GID cases.
- `chkdq()` adjusts block usage and enforces block hard/soft limits.
- `chkiq()` adjusts inode usage and enforces inode hard/soft limits.
- `quotaon()` opens and installs a quota file, marks it system, detects format, initializes grace periods, and attaches quota references to active writable vnodes.
- `quotaoff()` and `quotaoff_inchange()` disable quotas, suspend writes when needed, detach per-inode dquots, flush cached dquots, clear mount quota flags, and close the quota vnode.
- `getquota*`, `setquota*`, `setuse*`, and `getquotasize()` implement user-facing quota operations for both legacy 32-bit and native 64-bit forms.
- `qsync()` and `qsyncvp()` flush modified dquots globally or for one vnode.
- `dqinit()` and `dquninit()` initialize and tear down the global dquot hash/free-list system.
- `dqrele()` releases dquot references and writes dirty dquots before returning them to the free list.
- Soft updates helpers `quotaref()`, `quotarele()`, and `quotaadj()` provide deferred quota accounting support.

## Quota enforcement model
Each inode can hold up to `MAXQUOTAS` dquot pointers, currently user and group quotas. Positive allocation checks use privilege-aware enforcement unless `FORCE` is set or the caller can exceed quota. Negative changes never fail and clear prior warning flags.

Soft limits use time grace periods:
- Crossing a soft block limit initializes `dq_btime`.
- Crossing a soft inode limit initializes `dq_itime`.
- Remaining over the soft limit past the timer causes `EDQUOT`.
- Hard limits fail immediately.

If a later quota type fails during allocation, earlier successful quota adjustments are rolled back.

## Quota file lifecycle
`quotaon()` temporarily unbusies the mount while opening the quota file, then re-busies it and installs the vnode. It uses `QTF_OPENING` and `QTF_CLOSING` to serialize quota transitions and prevent `dqget()` from using half-open or closing quota files. Quota vnodes are marked `VV_SYSTEM`, allow recursive locking, and convert shared locks to exclusive to avoid deadlocks with directory inactive quota sync.

`quotaoff1()` clears per-vnode dquot references, flushes cached dquots for the quota file, clears `um_quotas[type]` before close, removes `VV_SYSTEM`, closes the file, and releases the saved credential.

## Dquot cache
The global cache uses:
- `dqhashtbl` keyed by quota vnode and id.
- `dqfreelist` for reusable unreferenced dquots.
- `dqhlock` protecting the hash table, free list, and dquot reference counters.
- Per-dquot `dq_lock` protecting fields and `DQ_LOCK/DQ_WANT` wait state.

`dqget()` checks the cache first, locks the quota vnode before adding a newly allocated dquot, reads the quota record from disk, initializes timers and `DQ_FAKE`, and wakes waiters. `dqsync()` writes modified records back using `VOP_WRITE` and secondary-write coordination.

## On-disk formats
- 32-bit quota files are arrays of native-endian `struct dqblk32`.
- 64-bit quota files have a `dqhdr64` header followed by network-byte-order `struct dqblk64` records.
- `dqopen()` detects the 64-bit header and sets `QTF_64BIT`.
- Conversion helpers clip 64-bit values to `UINT32_MAX` for 32-bit output.

## Dependencies
Uses mount state from `struct ufsmount`, vnode iteration, vnode I/O, credentials, privilege checks, soft updates hooks, mount suspension APIs, and quota definitions from `quota.h`.

## Research notes
The quota implementation is careful about mount busy state, quota vnode lock ordering, and dquot reference transitions. The most important invariants are that closing quota files are invisible to `dqget()`, dirty dquots are synced before becoming free, and inode quota pointers are detached before cached dquots for a quota file are flushed.
