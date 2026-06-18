# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_node.c

In-core PCFS node and vnode lifecycle management, node hash tables, metadata synchronization, truncation, media-change verification, and irrecoverable-state cleanup.

Key responsibilities:
- Initializes file and directory pcnode hash heads with `pc_init()`.
- Implements `pc_getnode()` to find or allocate active pcnodes, keyed by directory start cluster for directories and by directory-entry block/offset for regular files.
- Sets vnode operation vectors and vnode type, computes directory sizes from cluster chains, tracks file/root references, and holds the backing VFS.
- Implements `pc_rele()` to sync data, update directory entries, flush/invalidate cached pages, sync FAT, remove the node from hashes, drop reference counts, and free vnode/pcnode storage.
- Marks modification and access times through `pc_mark_mod()` and `pc_mark_acc()`.
- Implements `pc_truncate()` for file extension, shrink, zeroing partial clusters, page invalidation, and cluster freeing.
- Updates on-disk directory entries with `pc_nodeupdate()` and flushes file data plus metadata with `pc_nodesync()`.
- Verifies removable media state through `pc_verify()` using floppy change ioctls when enabled.
- Freezes damaged instances via `pc_mark_irrecov()` and forcibly tears down inactive nodes/FAT state through `pc_diskchanged()`.

Dependencies:
- Uses vnode, page, buffer, credential, device ioctl, and VFS reference infrastructure.
- Depends on allocation routines, FAT sync/invalidation, timestamp conversion, and global `pcnodes_lock`.

Notable risks:
- `PC_INVAL` nodes are retained enough for some stat-like behavior but reject normal I/O.
- Forced teardown rewires stale vnodes to `EIO_vfs` and must avoid nodes currently held or under release.
- `pc_rele()` can retry page invalidation if pages reappear during release.
- Metadata update skips FAT32 root because it has no directory entry; FAT12/FAT16 root update is a panic path.
