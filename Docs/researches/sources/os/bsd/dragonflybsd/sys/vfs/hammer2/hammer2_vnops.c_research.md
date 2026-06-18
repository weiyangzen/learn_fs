# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vnops.c

HAMMER2 vnode operation implementation for DragonFlyBSD VFS integration, covering file I/O, directory operations, namespace mutation, metadata changes, vnode lifecycle, kqueue, and special/FIFO vnode operation vectors.

Key responsibilities:
- Defines HAMMER2 VOP tables for regular vnodes, special-device vnodes, and FIFO vnodes.
- Handles vnode inactive/reclaim by disconnecting inodes, queuing unlinked inodes for delayed deletion, truncating cached buffers for deleted objects, and avoiding unsafe flushes during reclaim.
- Implements fsync by syncing logical file buffers, waiting for tracked writes, syncing inode metadata into chains, flushing inode-related chains, and clearing vnode dirty state when safe.
- Implements access, full getattr, lite getattr, setattr, advisory locking, open/close, ioctl, mountctl export setup, markatime, and kqueue filters.
- Implements regular-file and symlink reads/writes through DragonFly buffer-cache helpers, clustered reads/writes, `uiomovebp()`, file-size extension/truncation, resource-limit checks, and transaction interlocks.
- Implements directory readdir with synthetic `.`/`..` entries, directory cookies, XOP-backed scans, inode-vs-dirent result handling, and EOF offset management.
- Implements name resolution, `..` lookup, mkdir, create, mknod, symlink, hardlink, remove, rmdir, and rename using HAMMER2 inode locks, transactions, namecache updates, XOP workers, and kqueue notifications.
- Exposes strategy and bmap VOPs via functions implemented outside this file.

Important implementation details:
- Metadata mutation generally rejects read-only or emergency-mode mounts, starts a HAMMER2 transaction, locks relevant inodes, performs inode/dirent work, then completes the transaction with `HAMMER2_TRANS_SIDEQ`.
- `setattr` uses helper routines for flags, chown, chmod, and file-size changes; truncation and direct-data boundary crossing force `hammer2_inode_chain_sync()` because the chain topology must match the in-memory inode state.
- `hammer2_read_file()` takes inode/truncate locks, determines logical block geometry with `hammer2_calc_logical()`, uses `cluster_readx()`, and caps reads at file EOF.
- `hammer2_write_file()` handles append, pre-extension, partial-buffer read-before-write, `UIO_NOCOPY` pageout writes, direct/semi-sync writes under low-space pressure, and error rollback by truncating back to old EOF.
- Symlink creation creates an inode and directory entry first, then writes the target through the normal file-write path.
- Remove/rmdir use `hammer2_unlink_desc` XOPs and let `hammer2_inode_unlink_finisher()` update frontend inode disposition and possible vnode recycling.
- Rename locks source directory, target directory, source inode, and optional target inode; allocates a collision-safe target directory hash key; issues backend rename; updates frontend metadata/namecache after internal locks are released.
- Kqueue support reports readable bytes from `ip->meta.size`, write readiness, vnode event masks, and revoke EOF/NODATA handling.

Dependencies:
- Includes DragonFly kernel VFS, vnode, buffer-cache, mountctl, dirent, uio, kqueue, file, FIFO, and object-cache headers.
- Depends on HAMMER2 inode, transaction, XOP, chain, namecache, mount/PFS, buffer-cache, strategy, ioctl, and notification APIs from `hammer2.h`.
- Uses DragonFly helpers such as `vfsync`, `bio_track_wait`, `cluster_readx`, `cluster_write`, `bread_kvabio`, `getblk`, `nvtruncbuf`, `nvextendbuf`, `vop_helper_access`, `vop_helper_chown`, `vop_helper_chmod`, `lf_advlock`, and `cache_*`.

Notable risks:
- Lock ordering is subtle across vnode locks, inode locks, truncate locks, transactions, namecache operations, and XOP collection; rename in particular relies on pointer-order locking and cache updates after internal unlocks.
- Comments warn that some inode-chain synchronization for resize/direct-data transitions happens outside normal sync/fsync, creating crash-consistency edge cases.
- Symlink target write errors are explicitly ignored after the write path (`XXX handle error`), which can mask failure during creation.
- Atime is effectively unsupported: getattr reports atime from mtime and markatime only checks writability.
- File extension/truncation assumes VFS-level size interlocks; misuse from other paths can desynchronize buffer cache state and chain topology.
- Space-pressure handling can silently force `IO_DIRECT` for semi-synchronous writes, affecting performance and ordering.
