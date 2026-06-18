# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_quota.c

Implements Darwin/XNU generic quota-file and in-core dquot management: global dquot hash initialization, dquot lookup/allocation/reclaim, quota-file open/close synchronization, disk record lookup, dirty orphan sync, and user/kernel quota-structure conversion.

Key behavior:
- Defines global dquot cache state: hash table keyed by quota vnode and id, desired/actual dquot counts, free list, dirty orphan list, quota magic values, typed dquot allocator, and quota list/file locks.
- `dqhashinit` lazily initializes the dquot freelist, dirty list, and hash table under the quota list mutex; `dqisinitialized` reports readiness.
- Quota list locking tracks a mutation counter so lookup paths can detect that `dq_lock_internal` slept and invalidated assumptions.
- `dq_lock_internal` and `dq_unlock_internal` implement per-dquot logical locking with `DQ_LLOCK`/`DQ_LWANT` while coordinated by the global quota list mutex.
- `qf_get`/`qf_put` serialize quota-file opening and closing with `QTF_OPENING`, `QTF_CLOSING`, `QTF_WANTED`, vnode presence checks, refcount drain, sleeps, and wakeups.
- `qf_ref` and `qf_rele` protect quota files from `quota_off` while `dqget` may read or modify quota-file contents.
- `dqfileopen` validates quota file size/header, checks magic/version/maxentries, initializes grace periods, entry count, max entries, and hash-shift constants.
- `dqfileclose` rereads the quota-file header and writes back the current entry count using big-endian on-disk format.
- `dqget` first searches the in-core hash, removes cache hits from free/dirty lists when refcount rises from zero, otherwise allocates or recycles dquots under target limits, rechecks after sleeps/allocations, inserts the new dquot into the hash before disk initialization, and backs out cleanly on `dqlookup` failure.
- `dqlookup` performs open-addressed probing inside the quota file using `dqhash1`/`dqhash2`, reserves empty entries by writing a new id, increments file entry count, and converts existing big-endian `dqblk` records to host-endian fields.
- `dqrele` syncs modified dquots before returning them to the free list; `dqreclaim` avoids I/O and places modified zero-ref dquots on the dirty orphan list.
- `dqsync_orphans`, `dqsync`, and `dqsync_locked` flush modified dquot records back to their quota file, handling endian conversion and short-write detection.
- `dqflush` detaches all cached dquots associated with a quota vnode once they are unused.
- `munge_dqblk` converts between kernel `dqblk` and 64-bit user `user_dqblk`, with noted precision loss for time fields in one direction.

Dependencies:
- Uses vnode I/O (`VNOP_READ`, `VNOP_WRITE`, `vnode_size`), `uio` stack buffers, XNU locks/sleeps/wakeups, quota format definitions from `sys/quota.h`, byte swapping from `libkern/OSByteOrder.h`, and hash/list queue macros.

Research notes:
- The dquot cache is race-aware: many paths intentionally relookup after any operation that might sleep while the global lock is dropped.
- On-disk quota records are big-endian and probed by a quota-file-specific hash table, not by sequential scanning.
- Dirty dquots can become orphans when reclaimed without I/O, and the orphan list exists to flush them later for a particular quota file.
