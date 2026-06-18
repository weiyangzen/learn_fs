# File Research: sources/windows/winbtrfs/src/btrfs.h

## Role

`btrfs.h` is a public-domain, packed on-disk Btrfs format header for WinBtrfs. It defines constants, key/item type IDs, root IDs, feature flags, checksum/compression/encryption identifiers, block profile flags, and packed C structures matching Btrfs metadata and send-stream records.

## Constants And Feature Flags

- Defines superblock locations in `superblock_addrs`: 64 KiB, 64 MiB, 256 GiB, 1 PiB, then terminator 0.
- Defines core filesystem constants: `BTRFS_MAGIC`, `MAX_LABEL_SIZE`, `SUBVOL_ROOT_INODE`, and `BTRFS_LAST_FREE_OBJECTID`.
- Defines item type IDs for inodes, refs/extrefs, xattrs, orphan inodes, dir items/indexes, extent data/checksums/items/refs, roots/backrefs/refs, block groups, free-space records, device extents/items/stats, chunks, temp items, and subvolume UUID records.
- Defines well-known root IDs: root tree, extent tree, chunk tree, device tree, fs tree, tree dir, checksum tree, UUID tree, free-space tree, block-group tree, RAID-stripe tree, and data relocation root.
- Defines compression IDs for none, zlib, LZO, and ZSTD; encryption/encoding currently only none.
- Defines extent-data types: inline, regular, and prealloc.
- Defines block/profile flags for data, system, metadata, RAID0, RAID1, duplicate, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4.
- Defines special object IDs for free-space cache, extent checksum, balance item, and orphan inode.
- Defines inode flags, readonly inode flags, subvolume readonly flag, compatible-read-only flags, incompatibility flags through newer flags such as zoned, extent-tree-v2, raid-stripe-tree, and simple quota, and the seeding superblock flag.
- Defines checksum types: CRC32C, XXHASH, SHA256, and BLAKE2.

## Packed On-Disk Structures

All metadata structures are wrapped in `#pragma pack(push, 1)`/`#pragma pack(pop)` for byte-accurate disk layout.

- `BTRFS_UUID` wraps a 16-byte UUID.
- `KEY` is the common Btrfs key tuple: object ID, object type, offset.
- `tree_header`, `leaf_node`, and `internal_node` model B-tree node/leaf headers and child pointers.
- `DEV_ITEM` models device metadata including size, bytes used, I/O alignment, type, generation, device/group data, device UUID, and filesystem UUID.
- `superblock_backup` and `superblock` model the superblock, including checksum, UUIDs, addresses/generations/levels for key roots, byte counts, device item, label, cache/UUID tree generation, metadata UUID, system chunk array, and four backup roots.
- Directory and inode structures include `DIR_ITEM`, `BTRFS_TIME`, `INODE_ITEM`, `ROOT_ITEM`, `INODE_REF`, and `INODE_EXTREF`. A static assertion enforces `INODE_ITEM` size 0xa0.
- Chunk and extent structures include `CHUNK_ITEM`, `CHUNK_ITEM_STRIPE`, `EXTENT_DATA`, `EXTENT_DATA2`, `EXTENT_ITEM`, `EXTENT_ITEM2`, legacy `EXTENT_ITEM_V0`, `EXTENT_ITEM_TREE`, `TREE_BLOCK_REF`, `EXTENT_DATA_REF`, `EXTENT_REF_V0`, `SHARED_BLOCK_REF`, and `SHARED_DATA_REF`.
- Free-space and block metadata include `BLOCK_GROUP_ITEM`, `FREE_SPACE_ENTRY`, `FREE_SPACE_ITEM`, and `FREE_SPACE_INFO`.
- Subvolume/device/balance structures include `ROOT_REF`, `DEV_EXTENT`, `BALANCE_ARGS`, and `BALANCE_ITEM`.
- Device statistic indexes cover write, read, flush, corruption, and generation errors.

## Send Stream Definitions

- Defines Btrfs send command IDs from subvolume/snapshot creation through file operations, xattr operations, clone/truncate/chmod/chown/utimes, end, and update-extent.
- Defines send TLV IDs for UUID, transid, inode, size, mode, uid/gid, rdev, times, xattr name/data, path variants, offset/data, and clone metadata.
- Defines `BTRFS_SEND_MAGIC` and packed `btrfs_send_header`, `btrfs_send_command`, and `btrfs_send_tlv`.

## Consumers

- `btrfs.c` uses this file for superblock parsing/validation, feature masks, root/chunk/device scanning, object/key checks, filesystem label handling, checksum-size decisions, and Btrfs type-to-Windows attribute mapping.
- Other WinBtrfs source files depend on the same constants/structures for tree walking, writes, file info, send/receive, checksums, extent management, balance, scrub, and ioctl behavior.

## Notes

- The header intentionally mirrors on-disk structures rather than internal runtime structures; internal driver state is in `btrfs_drv.h`.
- It is licensed differently from the driver implementation: the file comment says this header alone is released into the public domain.
