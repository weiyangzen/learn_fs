# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.c

This file implements the normal TMPFS vnode operation vector. It covers namecache-aware lookup/create/remove/rename operations, regular I/O, VM/swap backing behavior, attributes, kqueue filters, reclaim/inactive handling, pathconf, and advisory locking.

Lookup uses DragonFly namecache operations: `tmpfs_nresolve` searches the directory RB tree and allocates a vnode for hits, while `tmpfs_nlookupdotdot` returns the parent vnode. Create, mknod, mkdir, and symlink all call `tmpfs_alloc_file`, then update the namecache and emit kqueue notifications.

Open restores any pages previously moved into the node’s backing aobj. Close updates timestamps. Access enforces read-only mount and immutable rules before calling helper permission logic. Getattr/getattr_lite project tmpfs node fields into VFS attribute structures. Setattr sequences flag, size, ownership, mode, and time updates, restores saved pages before resize, updates timestamps, and emits knotes.

Read first tries `vop_helper_read_shortcut`, then restores saved pages if needed and reads through KVABIO buffer-cache blocks, optionally using clustered reads. Write enforces file-size limits and `RLIMIT_FSIZE`, supports append, resizes as needed, fills gaps safely through `bread_kvabio`, writes through buffer-cache paths chosen by memory pressure and `tmpfs_bufcache_mode`, handles UIO_NOCOPY/pageout cases specially, updates SUID/SGID, timestamps, size, and knotes.

`tmpfs_strategy` sends regular-file pageout I/O to the swap pager through the node’s aobj. If there is no swap, write pages are simply marked as needing commit. Completion clears or restores commit state without propagating swap errors to the buffer. `tmpfs_bmap` presents logical contiguity for clustering.

Remove, link, rename, rmdir, and symlink maintain directory RB trees, link counts, parent pointers, deleted-directory behavior, namecache state, and vnode notifications. Rename uses `tmpfs_lock4` to avoid directory lock-order reversals and handles target replacement rules for files and directories.

Readdir synthesizes `.` and `..`, uses cookie-ordered RB traversal for real entries, returns optional NFS cookies, and marks access. Readlink copies the stored target string. Inactive recycles deleted nodes and moves live regular-file pages from vnode object into the node backing aobj so vnode reclamation does not discard cached tmpfs data. Reclaim clears vnode/node associations and frees nodes whose link count is zero.

The file also supports mountctl export updates, debug printing, POSIX pathconf values, advisory locks through `lf_advlock`, and kqueue filters for read/write/vnode events. The exported `tmpfs_vnode_vops` wires these operations into DragonFly’s VFS.
