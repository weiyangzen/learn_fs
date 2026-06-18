# File Research: sources/teaching/os161/kern/fs/semfs/semfs_obj.c

Implements constructors, destructors, and table insertion for `semfs` backing objects.

Key functions:
- `semfs_sem_create` allocates a semaphore object, creates a per-object lock and CV named from the file name, initializes count to 0, and marks it unlinked and without vnode.
- `semfs_sem_destroy` destroys CV, lock, and allocation.
- `semfs_sem_insert` requires `semfs_tablelock`, reuses the first NULL table slot, or appends to the semaphore array. It returns `ENOSPC` before colliding with `SEMFS_ROOTDIR`.
- `semfs_direntry_create` duplicates the name and stores the semaphore number.
- `semfs_direntry_destroy` frees the name and entry.

Notable invariants:
- Semaphore table slots may be sparse after unlink/reclaim.
- Directory entries own their copied names.
- Lock/CV creation is failure-cleaned in reverse allocation order.
