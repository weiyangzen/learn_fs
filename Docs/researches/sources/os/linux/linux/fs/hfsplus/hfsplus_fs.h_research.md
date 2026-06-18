# File Research: sources/os/linux/linux/fs/hfsplus/hfsplus_fs.h

## Role

Central private header for the Linux HFS+ driver. It defines in-memory B-tree, superblock, inode, finder, and readdir state; mount/runtime flags; compatibility aliases; ioctl constants; cross-file function prototypes; and small inline helpers used throughout the HFS+ implementation.

## Key Definitions

- `struct hfs_btree`: in-memory HFS+ B-tree descriptor with backing inode, key comparator, root/leaf/free-node counters, node geometry, tree mutex, pages-per-node metadata, and a 256-bucket hash of cached `hfs_bnode` objects.
- `struct hfs_bnode`: cached B-tree node with tree pointer, node IDs/linkage, record count, node type/height, lock/error/new/dirty/deleted bits, wait queue, refcount, page offset, and flexible page array.
- `struct hfsplus_sb_info`: filesystem private superblock state derived from the on-disk volume header plus runtime state:
  - active and backup volume header buffers;
  - extents, catalog, and attributes B-trees;
  - allocation file and hidden directory inodes;
  - NLS table, partition/session layout, block offset, minimum I/O size, allocation geometry;
  - mutable `free_blocks`, `next_cnid`, file/folder counts guarded by `alloc_mutex` and `vh_mutex`;
  - creator/type defaults, umask/uid/gid overrides, mount flags, delayed sync work, and RCU release.
- `struct hfsplus_inode_info`: HFS+-private inode state for resource forks, extent caches, create date, hard-link ID, HFS+/BSD flags, subfolder count, open-directory tracking, physical size, and embedded VFS inode.
- `struct hfs_find_data`: B-tree search cursor carrying caller-provided keys plus located node, record number, key offset/length, and entry offset/length.
- `struct hfsplus_readdir_data`: directory iteration state linked through the inode-private open directory list.
- Runtime flags include backup-header write, nodecompose, force, HFSX, casefold, nobarrier, uid override, and gid override.
- Inode dirty flags distinguish catalog, extent, allocation-file, and attributes-tree metadata dirtiness.
- `HFSPLUS_IOC_BLESS` defines the HFS+-specific boot-blessing ioctl.

## Cross-File API Surface

The header exposes the driver’s internal subsystem contracts:

- Attributes: key comparison/building, lookup, create/delete/replace, delete-all, allocation/free of attribute entries, and cache lifecycle.
- Bitmap/allocation: allocation-block allocate/free.
- B-tree and B-node: tree open/close/write, B-tree bitmap reserve/alloc/free, node I/O, node hash lookup, node create/free/get/put, and node bounds helpers.
- B-record/B-find: record length/key helpers, insert/remove/read/goto, cursor init/exit, and record search strategies.
- Catalog: key comparison/building, permission serialization, catalog lookup/create/delete/rename.
- Extents: key comparison, extent writeback, block mapping, fork free, file extend, and file truncate.
- Inode/VFS: address-space ops, dentry ops, inode creation/deletion, fork read/write, catalog inode read/write, getattr, fsync, and file attributes.
- Options, partition map, superblock commit/dirty handling, Unicode conversion/comparison/hash, and wrapper block I/O.

## Inline Logic

- `HFSPLUS_SB()` and `HFSPLUS_I()` recover private superblock and inode structures.
- `hfsplus_mark_inode_dirty()` sets an HFS+-specific metadata dirty bit and marks the VFS inode dirty.
- `hfsplus_min_io_size()` returns the larger of probed minimum I/O size and the HFS+ sector size.
- `hfsplus_cat_thread_size()` computes variable-length catalog-thread record size.
- Time helpers convert between HFS+ 1904-based timestamps and Unix timestamps. The comment documents Linux’s unsigned-wrap behavior that maps low on-disk values into the 2040-2106 range.
- `hfsplus_btree_lock_class()` maps catalog/extents/attributes B-tree CNIDs to lockdep nested mutex subclasses and `BUG()`s for unexpected tree IDs.
- `is_bnode_offset_valid()` validates a B-node offset against node size and logs corrupt requests.
- `check_and_correct_requested_length()` clamps B-node read/write length at node bounds and logs the correction.

## Dependencies

Includes Linux filesystem, mutex, buffer-head, block-device, and fs-context headers plus `hfsplus_raw.h`. It relies on common on-disk HFS/HFS+ definitions from `linux/hfs_common.h` via `hfsplus_raw.h`.

## Research Notes

This header is the HFS+ driver’s main coupling point. Most implementation files depend on its structure layouts, dirty-bit model, and prototypes. The inline B-node bounds helpers are security-relevant defensive code because corrupted on-disk B-tree offsets and lengths are checked centrally before node I/O.
