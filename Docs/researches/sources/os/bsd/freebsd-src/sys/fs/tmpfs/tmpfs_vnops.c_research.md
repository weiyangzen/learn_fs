# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.c

FreeBSD tmpfs vnode operations implementation.

Key responsibilities:
- Implements tmpfs lookup, creation, mknod, open/close, access, stat/getattr/setattr, read/write, fsync, unlink/link/rename, mkdir/rmdir, symlink/readlink, readdir, inactive/reclaim, pathconf, file-handle export, whiteouts, reverse name lookup, extended attributes, and `FIOSEEKDATA`/`FIOSEEKHOLE`.
- Defines `tmpfs_vnodeop_entries`, the main tmpfs VOP vector, and `tmpfs_vnodeop_nonc_entries`, the non-namecache lookup override.
- Integrates FreeBSD fast path lookup and SMR paths through `tmpfs_fplookup_vexec`, `tmpfs_fplookup_symlink`, and `tmpfs_read_pgcache`.
- Uses tmpfs VM objects for regular file data via `uiomove_object`, `tmpfs_reg_resize`, `tmpfs_reg_punch_hole`, swap-pager hole/data seeking, and vnode object lifecycle hooks.
- Maintains tmpfs directory state, link counts, parent pointers, whiteout entries, and namecache notifications during mutating operations.
- Implements in-memory extended attributes with per-mount memory accounting and credential checks.

Dependencies:
- Depends on FreeBSD VFS/vnode, namecache, lock, SMR, MAC, audit, fileops, extattr, and VM/swap pager APIs.
- Depends heavily on tmpfs internal helpers and state from `fs/tmpfs/tmpfs.h`, including node locking, allocation, directory entry management, time updates, quota/page accounting, and vnode allocation/free routines.
- Exports selected entry points declared in `tmpfs_vnops.h`.

Notable risks:
- Rename is lock-order sensitive and uses restart logic plus a `vfs.tmpfs.rename_restarts` counter; changes here can easily introduce deadlocks or stale vnode/namecache state.
- SMR fast paths require `VP_TO_TMPFS_NODE_SMR`, link target storage, object state, and vnode doom checks to remain valid without ordinary vnode locking.
- Extended attributes are in-memory only and separately accounted; incorrect `diff` accounting can leak or overcommit tmpfs memory.
- Directory removal and rename must handle whiteout-only directories carefully to avoid leaking whiteout entries.
- `tmpfs_vptocnp` scans mounted tmpfs nodes for non-directory reverse lookup, so it is sensitive to node reference, attachment, and reclaim races.
