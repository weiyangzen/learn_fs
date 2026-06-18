# File Research: sources/os/linux/linux/fs/ntfs/inode.c

## Purpose
Implements NTFS inode lifecycle and metadata synchronization: VFS inode cache identity, normal/attribute/index inode instantiation, mount-time `$MFT` bootstrap, extent inode management, eviction/deletion, mount option reporting, truncation/initialized-size updates, MFT record writeback, and attribute pread/pwrite.

## Key Elements
`ntfs_test_inode()` and `ntfs_init_locked_inode()` allow `iget5_locked()` to distinguish normal inodes from fake attribute and index inodes that share the same MFT number but differ by NTFS attribute type/name. `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` instantiate those three inode classes and dispatch to specialized readers.

`ntfs_read_locked_inode()` decodes a normal MFT record: sequence number, link count, `$STANDARD_INFORMATION` timestamps and flags, optional `$ATTRIBUTE_LIST`, EA presence and WSL metadata, directory `$INDEX_ROOT` geometry, unnamed `$DATA` size/run attributes, reparse symlink mode, compression/sparse/encryption state, inode operations, immutable system-file state, and block accounting. It has special handling for `$Extend` metadata indexes such as `$Reparse` and `$ObjId`.

`ntfs_read_locked_attr_inode()` mirrors base inode ownership/times into fake attribute inodes, validates attribute flags, initializes resident or non-resident sizes, compression geometry, block counts, address-space ops, and holds a reference to the base inode. `ntfs_read_locked_index_inode()` performs the equivalent setup for `$INDEX_ALLOCATION`, including `$INDEX_ROOT` validation, optional missing allocation for small indexes, non-resident allocation checks, and `$BITMAP` size consistency.

`ntfs_read_inode_mount()` bootstraps `$MFT` before normal MFT mapping is available. It reads record 0 directly from the block device, applies MST fixups, validates `$MFT`, loads any attribute list directly, then builds the full `$MFT/$DATA` runlist extent by extent. Once the first runlist extent is known, it calls the normal inode reader and then restores `$MFT` as a protected internal inode with empty VFS operations.

Writeback flows through `__ntfs_write_inode()`: attribute inodes are cleaned through their base inode, base inodes update dirty mapping pairs, synchronize `$STANDARD_INFORMATION`, optionally update parent FILE_NAME index entries, write their own MFT record, map and write dirty extent MFT records, and mark the volume erroneous on non-memory failures. `ntfs_inode_sync_filename()` updates parent directory index entries with current flags, sizes, reparse tag, and times.

The lower part of the file manages extent inodes, attribute lists, MFT record free-space creation, and attribute raw I/O. `ntfs_inode_add_attrlist()` builds an in-memory and on-disk `$ATTRIBUTE_LIST`, freeing MFT record space by moving movable attributes if needed and rolling back on failure. `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` provide resident/non-resident attribute I/O for EA, bitmap, and index code, using page cache for normal writes and optional synchronous bio writes for non-resident attributes.

## Dependencies And Integration
Includes NTFS allocation, time conversion, core NTFS state, index, attribute-list, reparse, EA, attribute, iomap, and object-id headers. It supplies helpers used across directory, file, index, EA, MFT, and superblock code, and it selects `ntfs_dir_ops`, `ntfs_file_ops`, symlink/special ops, `ntfs_aops`, and `ntfs_mft_aops`.

## Behavior/Risks
This file is lock-sensitive. It defines separate lockdep classes for attribute, attribute-list, extent, MFT, and directory mapping locks; many paths require `mrec_lock`, `extent_lock`, or runlist locks in a fixed order. Corruption handling generally logs a chkdsk recommendation and sets volume errors except for unsupported features or memory pressure. Eviction deletes unlinked base inodes by freeing clusters, extent MFT records, and the base MFT record; dirty live inodes are committed before memory cleanup. Attribute raw writes reject compressed non-resident growth and encrypted non-resident enlargement.
