# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnops.c

Purpose: Implements NetBSD vnode operations for CHFS files, directories, symlinks, special nodes, and fifos.

Major VOPs:
- Namespace: `chfs_lookup`, `chfs_create`, `chfs_mknod`, `chfs_remove`, `chfs_link`, `chfs_rename`, `chfs_mkdir`, `chfs_rmdir`, `chfs_symlink`, `chfs_readdir`, `chfs_readlink`.
- Metadata/access: `chfs_open`, `chfs_close`, `chfs_access`, `chfs_getattr`, `chfs_setattr`, `chfs_chmod`, `chfs_chown`.
- IO: `chfs_read`, `chfs_write`, `chfs_fsync`, `chfs_strategy`, `chfs_bmap`.
- Lifecycle: `chfs_inactive`, `chfs_reclaim`, `chfs_advlock`.
- Operation vectors: `chfs_vnodeop_entries`, `chfs_specop_entries`, `chfs_fifoop_entries`.

Important behavior:
- Lookup handles `.` and `..` synthetically, consults namecache, then searches CHFS dirent lists.
- Create/mkdir/mknod/symlink are built on `chfs_makeinode`; mknod and short symlinks store payload as data nodes.
- Remove/rmdir/link/rename use append-log dirent operations in `chfs_do_unlink` and `chfs_do_link`.
- Regular-file read/write mostly use NetBSD UBC/genfs/UFS-style buffered paths; actual page IO is handled in `chfs_strategy`.
- `chfs_strategy` reads through `chfs_read_data` or writes a fresh flash data node and adds it to the inode fragment tree.
- `chfs_readdir` synthesizes `.` and `..`, then emits live dirents using offset constants.
- Reclaim marks vnode cache checked-absent, kills fragments, frees dirents, purges namecache, releases device vnode, destroys genfs node, and returns inode to pool.

Dependencies:
- Heavy use of NetBSD VFS, UBC, genfs, UFS helper functions, kauth, and CHFS inode/write/read helpers.
- Operation vectors delegate special/fifo behavior to genfs/specfs/fifofs where appropriate.

Research notes:
- `chfs_sync`/fsync semantics are minimal; fsync flushes vnode buffers but not a broad mount-level sync implementation.
- Rename is implemented as link-new then unlink-old and is relatively simple compared with full POSIX edge-case handling.
- Short symlink threshold is hardcoded at 100 with TODO comments.
