# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vnops.c

HAMMER1 vnode operation implementation for regular files, directories, symlinks, device nodes, FIFOs, strategy I/O, namespace mutation, and kqueue notification.

Key responsibilities:
- Defines the HAMMER vnode operation vectors for normal vnodes, special-device vnodes, and FIFO vnodes.
- Implements `fsync` with multiple policy modes, including full flush, asynchronous relaxation, REDO/UNDO FIFO flushing for version-four filesystems, and an ignore mode.
- Implements regular-file `read` and `write` through the VM shortcut path and buffer cache, using variable HAMMER block sizes, clustering, sequential heuristics, large-I/O signal checks, atime/mtime updates, and write-size/rlimit checks.
- Generates REDO records for fast-fsync write/truncate paths and disables REDO tracking when heuristic limits are exceeded.
- Implements POSIX metadata and namespace VOPs: access, advisory locks, open/close, create, mkdir, mknod, link, symlink, remove, rmdir, rename, whiteout, getattr, setattr, readlink, readdir, lookup, and lookup-dotdot.
- Supports historical/as-of lookups and PFS access through `@@` name extensions, including special `@@PFS` symlink expansion.
- Implements strategy read/write and bmap support for file data, with direct I/O shortcuts for aligned zone-large data, indirect/double-buffered reads, sparse-hole zero-fill, truncation interlocks, and bulk in-memory record installation for writes.
- Provides `mountctl`, ioctl dispatch, and kqueue filter operations for read/write/vnode events.

Important implementation details:
- Most metadata-changing paths acquire `hmp->fs_token`, start a HAMMER transaction, modify inode or directory records, then release the token after transaction completion.
- Directory lookup and unlink use HAMMER directory name keys as chained hash ranges and merge in-memory records with on-disk records via cursor iteration.
- `hammer_dounlink()` centralizes remove/rmdir/whiteout target resolution, type validation, directory emptiness checks, directory-entry deletion, cache unlinking, and vnode delete notification.
- `rename` first removes or ignores the target, links the source inode into the target directory, updates the moved inode parent/ctime, then removes the old directory entry.
- `getattr` synthesizes snapshot-stable atime/mtime for read-only/historical inodes and reports fsids that vary by as-of TID while remaining tied to the PFS shared UUID.
- Strategy read handles gaps, frontend/backend truncation state, on-disk direct read eligibility, and post-read cache-node hints for file and parent directory traversal.
- Strategy write installs new bulk records and queues direct writes; HAMMER does not overwrite existing data blocks in-place.

Dependencies:
- Includes DragonFly VFS, namecache, buffer-cache, FIFO, kqueue, mountctl, VM, transaction, cursor, inode, blockmap, flusher, REDO, and HAMMER object APIs through `hammer.h`.
- Uses vnode helpers such as `vop_helper_read_shortcut`, `vop_helper_access`, `vop_helper_chown`, `vop_helper_chmod`, `vfsync`, `cluster_readx`, `cluster_write`, `nvextendbuf`, and `nvtruncbuf`.
- Depends on HAMMER transaction, cursor, inode, record, buffer, direct-I/O, and flusher primitives defined elsewhere in the HAMMER1 implementation.

Notable risks:
- The file has many cross-locking paths between vnode locks, `fs_token`, cursor locks, inode locks, buffer locks, and flusher activity; the explicit `EDEADLK` retry paths are critical.
- Several comments acknowledge broken or weakened atomicity around rename/unlink deadlock avoidance and truncate/backend flushing.
- REDO correctness depends on subtle interaction between write-generated records, truncate records, `HAMMER_INODE_REDO`, `HAMMER_INODE_RDIRTY`, and flusher termination records.
- Variable block sizes around the `HAMMER_XDEMARC` boundary require careful bmap, clustering, truncation, and buffer-cache sizing.
- Snapshot/as-of and PFS path syntax is embedded in normal name lookup and symlink handling, so changes to lookup parsing can affect user-visible snapshot access.
- Dynamic vnode references around inactive/reclaim and notification paths are race-prone and handled with repeated `hammer_get_vnode()` checks.
