# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vnops.c

Read completely: 1933 lines.

Implements generic UFS vnode operations for metadata, namespace mutation, directory reads, symlinks, locking, strategy I/O dispatch, special/FIFO wrappers, kqueue filters, and inode creation.

Core behavior:
- `ufs_itimes()` applies pending access/change/update timestamp flags, handles ext2 separately, marks lazy or modified state, updates nanosecond timestamps, and increments modification revision.
- Create/mknod/mkdir/symlink paths allocate inodes through vtable hooks, initialize uid/gid/mode/link counts, charge quotas, write inode state before directory entries, and update parent directories through `ufs_direnter()`.
- `ufs_open()`, `ufs_access()`, `ufs_getattr()`, and `ufs_setattr()` enforce append/immutable/read-only checks, expose inode metadata, perform truncation, timestamp updates, chmod/chown, and emit vnode notifications.
- `ufs_chown()` transfers quota usage from old uid/gid to new uid/gid with rollback on failure.
- `ufs_remove()`, `ufs_link()`, `ufs_rename()`, and `ufs_rmdir()` implement hard links and namespace removal/rename, including sticky directory checks, link-count staging, directory cycle prevention, `..` rewriting, target replacement, source relookup, cache purges, and error rollback.
- `ufs_readdir()` converts on-disk `struct direct` entries to userland `struct dirent`, avoids partial entries, validates record lengths and slash-free names, updates offsets/eof, and marks access time.
- `ufs_readlink()` serves short symlinks from inode block-pointer storage or delegates to `VOP_READ()` for long symlinks.
- `ufs_lock()`, `ufs_unlock()`, and `ufs_islocked()` wrap the inode `rrwlock`.
- `ufs_strategy()` maps logical buffers through `VOP_BMAP()`, clears holes, and sends real I/O to the device vnode.
- Special-device and FIFO wrappers mark inode timestamps before delegating to `spec_*` or `fifo_*`.
- `ufs_pathconf()` returns POSIX path limits and transfer alignment; `ufs_advlock()` delegates byte-range locks to `lf_advlock()`.
- `ufs_makeinode()` is the shared file/symlink inode creation helper.
- Kqueue support installs read/write/vnode filters and reports data availability, write readiness, vnode notes, and revoke EOF/oneshot state.

Integration and risks:
- Rename is the most complex path: it relies on staged extra link counts, `IN_RENAME`, `vfs_relookup()`, `ufs_checkpath()`, and careful vnode release/unlock behavior.
- Quota, link-count, and directory-entry updates must roll back coherently on write or allocation errors.
- `ufs_strategy()` depends on `ufs_bmap()` and buffer-cache hole semantics.
- Kqueue and timestamp side effects depend on every metadata mutation emitting the right `VN_KNOTE()` and inode flags.
