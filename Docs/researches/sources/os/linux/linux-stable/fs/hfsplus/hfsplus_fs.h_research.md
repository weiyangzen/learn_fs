# File Research: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_fs.h

## Role

Central private header for the Linux HFS+ driver. It defines in-memory B-tree, superblock, inode, finder, and readdir state; mount/runtime flags; compatibility aliases; ioctl constants; cross-file function prototypes; and small inline helpers used by nearly every HFS+ implementation file.

## Key Definitions

- `struct hfs_btree`: in-memory representation of an HFS+ B-tree, including backing inode, key comparator, root/leaf/free-node counters, node sizing, tree mutex, pages-per-node metadata, and a hash table of cached `hfs_bnode` objects.
- `struct hfs_bnode`: in-memory B-tree node with tree pointer, linkage fields, record count, node type/height, flags, wait queue, refcount, page offset, and flexible page array.
- `struct hfsplus_sb_info`: filesystem private superblock state derived from the on-disk volume header plus runtime state:
  - volume header buffers and backup header buffers;
  - extents/catalog/attributes B-trees;
  - allocation file and hidden directory inodes;
  - NLS table;
  - partition/session/block layout;
  - immutable allocation geometry;
  - mutable `free_blocks`, `next_cnid`, file/folder counts;
  - mount flags and delayed sync work state.
- `struct hfsplus_inode_info`: private inode state for resource forks, extent caches, create date, link id, BSD user flags, subfolder count, open directory tracking, physical size, and embedded VFS inode.
- `struct hfs_find_data`: B-tree search cursor carrying caller-owned keys plus located node, record number, key offset/length, and entry offset/length.
- `struct hfsplus_readdir_data`: open-directory iteration state linked into inode-private open-dir tracking.
- Runtime flags include backup-header write, nodecompose, force, HFSX, casefold, nobarrier, uid override, and gid override.
- Inode flags include resource fork, catalog dirty, extents dirty, allocation dirty, and attributes dirty.
- `HFSPLUS_IOC_BLESS` defines the HFS+-specific boot-blessing ioctl.

## Cross-File API Surface

The header exposes the driver’s internal subsystem contracts:

- Attributes: key comparison/building, lookup, create/delete/replace, delete-all, cache lifecycle.
- Bitmap/allocation: block allocate/free.
- B-tree and B-node: open/close/write, bitmap reserve/alloc/free, node I/O, hash lookup, create/free/get/put.
- B-record/B-find: record insert/remove/read/goto and search routines.
- Catalog: key comparison/building, permissions serialization, catalog lookup/create/delete/rename.
- Extents: key comparison, extent writeback, block mapping, fork free, file extend/truncate.
- Inode/VFS: address-space ops, dentry ops, inode creation/deletion, fork read/write, catalog inode read/write, getattr/fsync/fileattr.
- Options, partition map, superblock, Unicode conversion/comparison/hash, and wrapper block I/O.

## Inline Logic

- `HFSPLUS_SB()` and `HFSPLUS_I()` retrieve private superblock and inode structures.
- `hfsplus_mark_inode_dirty()` sets a specific metadata dirty bit and marks the VFS inode dirty.
- `hfsplus_min_io_size()` returns the larger of the probed minimum I/O size and HFS+ sector size.
- Time helpers convert between HFS+ 1904-based timestamps and Unix timestamps. The comment documents the Linux behavior of treating low on-disk values as future 2040-2106 values due to unsigned 32-bit wrap behavior.
- `hfsplus_btree_lock_class()` maps catalog/extents/attributes B-tree CNIDs to lockdep nested mutex subclasses and `BUG()`s for unexpected tree IDs.
- `is_bnode_offset_valid()` validates a requested B-node offset against node size and logs invalid requests.
- `check_and_correct_requested_length()` clamps B-node read/write lengths that would cross node bounds and logs the correction.

## Dependencies

Includes Linux filesystem, mutex, buffer-head, block-device, and fs-context headers plus `hfsplus_raw.h`. It relies on on-disk HFS+ types and constants supplied through Linux HFS common raw definitions.

## Research Notes

This header is the driver’s main coupling point: most implementation files depend on its structures, flags, and prototypes. The inline B-node bounds helpers are notable because they centralize defensive behavior for corrupted on-disk B-tree offsets/lengths. The header also makes the metadata dirty-bit model explicit: individual metadata files are normal inodes, but dirtiness is tracked with HFS+-specific bits so sync/fsync can flush the correct B-tree or allocation file.
