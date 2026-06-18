# File Research: sources/teaching/os161/kern/fs/semfs/semfs_vnops.c

Implements vnode operations for `semfs` root directory and semaphore files.

Semaphore-file semantics:
- `read` is semaphore `P`: consumes `uio_resid` units from `sems_count`, blocking on the CV while count is zero. It advances offset/resid but transfers no actual bytes.
- `write` is semaphore `V`: increments count by `uio_resid`, detects unsigned overflow with `EFBIG`, wakes waiters, and consumes the whole write.
- `truncate` resets the count to `len`, rejecting negative lengths and lengths greater than unsigned max.
- `stat` reports `st_size` as current count, `st_nlink` from linked state, mode `S_IFREG | 0666`, inode as semaphore number.
- Semaphore vnodes are non-seekable.

Directory semantics:
- Root directory is read-only for open, mode `S_IFDIR | 1777`, `st_size` is number of directory-entry array slots.
- `getdirentry` returns the name at offset-as-index, with EOF when offset is past the directory array.
- `creat` creates or opens a named semaphore, handles `.`/`..`, optional exclusive create, sparse directory slots, table insertion, vnode creation, and cleanup on failure.
- `remove` unlinks a semaphore. If no vnode exists, it also removes the semaphore table slot and destroys the object; otherwise the object survives until reclaim.
- `lookup` maps `.`/`..` to the root vnode and names to semaphore vnodes.
- `lookparent` returns the same root vnode and copies the final component because subdirectories are unsupported.

Vnode lifecycle:
- `semfs_getvnode` searches the live vnode array under `semfs_tablelock`, increments refs if found, or creates a new vnode and marks `sems_hasvnode`.
- `semfs_reclaim` refuses if refcount rose above one, removes the vnode from the vnode array, clears `sems_hasvnode`, and destroys unlinked semaphore objects.

Notable locking:
- Directory namespace is protected by `semfs_dirlock`.
- Vnode/semaphore tables are protected by `semfs_tablelock`.
- Semaphore count/link state is protected by each semaphore lock.
