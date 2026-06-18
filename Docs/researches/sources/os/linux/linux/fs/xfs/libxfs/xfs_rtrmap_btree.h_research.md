# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.h

## Purpose

`xfs_rtrmap_btree.h` declares realtime rmap btree APIs and root-layout helpers for in-core, on-disk, staged, and optional in-memory realtime rmap btrees.

## Main Content

- Defines `XFS_RTRMAP_BLOCK_LEN` as the CRC long btree block header length.
- Declares live/staged cursor, staged commit, max-record, max-level, reserve, size, create, and realtime-superblock initialization helpers.
- Provides in-core address helpers for records, low keys, high keys, and pointers.
- Provides on-disk dinode-root address helpers for records, keys, and pointers.
- Provides root size calculators for in-core and on-disk root formats.
- Declares inode format/load, disk conversion, and flush helpers.
- Declares optional in-memory realtime rmap btree cursor and initialization helpers.
- Declares `xfs_rtrmap_highest_rgbno`.

## Key Interfaces and Invariants

- Internal nodes store two rmap keys per pointer because the tree is overlapping.
- In-core and on-disk roots have different headers and must use the matching size/address helpers.
- In-memory helper declarations are present regardless of build guards in this header; definitions depend on `CONFIG_XFS_BTREE_IN_MEM`.
- Root space must fit inside the metadata inode data fork.

## Dependencies

Depends on realtime rmap on-disk structures, btree cursor types, realtime group state, optional xfbtree state, and inode/dinode definitions supplied by surrounding XFS headers.
