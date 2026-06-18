# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_format.h

## Scope

This header defines the on-disk formats shared by XFS directories and attributes: DA node headers, v2/v3 directory block/data/leaf/free formats, shortform directory records, data entry/free record layouts, single-block directory tails, attribute shortform and leaf records, remote attribute block headers, namespace flags, and parent pointer records.

## Main Format Areas

- DA common structures: v2/v3 magic numbers, `xfs_da_blkinfo`, `xfs_da3_blkinfo`, node headers, node entries, and max depth.
- Directory v2/v3 formats: single-block, data, leaf1, leafn, and free block magic values plus CRC-era headers.
- Directory file types: on-disk `XFS_DIR3_FT_*` values and string table macro.
- Directory shortform: `xfs_dir2_sf_hdr`, `xfs_dir2_sf_entry`, 32-bit vs 64-bit inode packing helpers, offset helpers, and first-entry accessor.
- Directory data blocks: bestfree slots, active entry layout, unused/free entry layout, alignment constants, address-space partitioning, and tag accessors.
- Directory leaf/free/block format: leaf entries, leaf tail bestcount, free block bests array, single-block embedded leaf tail and accessor.
- Attribute formats: shortform header/entries, attr leaf header, entry array, local and remote name/value records, v3 attr leaf header, namespace/incomplete flags, and entry-size helpers.
- Remote attribute format: `xfs_attr3_rmt_hdr`, CRC offset, buffer payload sizing declaration.
- Parent pointer format: `xfs_parent_rec` storing parent inode and generation.

## Notable Layout Rules

Directory address space is partitioned into data, leaf, and free spaces separated by 32 GiB regions. Directory data entries are 8-byte aligned and carry a trailing tag equal to the entry offset. Single-block directories embed the leaf array and tail at the end of the data block.

Attribute leaf blocks pack sorted entries from the front and name/value storage from the back. The freemap tracks only the largest free regions, so compaction is sometimes required. Attribute local/remote entry size helpers deliberately preserve historical flex-array padding formulas from the on-disk ABI.

## Dependencies

This header is consumed by nearly all XFS directory and attribute implementation files, the DA Btree layer, remote attribute code, parent pointer code, verifiers, and userspace repair/tooling that must understand the same on-disk ABI.

## Risks And Invariants

- This file describes on-disk ABI. Structure layout, magic values, alignment, padding formulas, and field sizes cannot be changed casually.
- v3 CRC headers must remain first-field compatible where generic DA code treats them as `xfs_da_blkinfo`.
- Attr namespace and incomplete bits control user-visible xattrs, parent pointers, and crash recovery semantics.
- Directory file type additions require on-disk feature support.
- Shortform directory and attribute structures are variable length; callers must use accessors instead of assuming fixed offsets.
