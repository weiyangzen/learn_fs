# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfs.h

## Scope

This report covers the complete `btrfs.h` header. It is the packed on-disk format definition header for the WinBtrfs/ReactOS Btrfs driver. It defines Btrfs constants, object IDs, item type IDs, feature flags, checksum types, block group profiles, file types, and packed C structs corresponding to superblocks, tree headers, keys, inode/root/chunk/extent/free-space/device/balance/send-stream records.

## Primary Responsibilities

- Defines the physical superblock mirror offsets in `superblock_addrs`.
- Defines Btrfs magic, maximum label size, special inode/object IDs, root object IDs, item type numbers, compression/encryption/encoding identifiers, extent data types, block profile flags, inode/subvolume flags, compat-ro and incompat feature flags, superblock flags, orphan object ID, and checksum type IDs.
- Declares packed structures that map directly to Btrfs on-disk byte layouts.
- Provides Btrfs send-stream command and TLV IDs used by send/receive code.
- Uses `#pragma pack(push, 1)` / `#pragma pack(pop)` so fields match disk layout without compiler padding.

## Format Structures

Core identity and key structures:
- `BTRFS_UUID` is a 16-byte UUID wrapper.
- `KEY` is the standard Btrfs tree key: object ID, item type, and offset.
- `tree_header`, `leaf_node`, and `internal_node` describe serialized tree blocks and their item pointers.

Superblock and device structures:
- `DEV_ITEM` represents device metadata stored in the superblock and chunk tree.
- `superblock_backup` stores backup root addresses/generations and size information.
- `superblock` is the full Btrfs superblock layout, including checksum, UUIDs, generation, root addresses, device item, label, feature flags, system chunk array, backup roots, and reserved space.

Filesystem object structures:
- `DIR_ITEM` stores directory/xattr directory items with inline variable-length name/data.
- `BTRFS_TIME` stores seconds and nanoseconds.
- `INODE_ITEM` stores inode stat-like fields, Btrfs inode flags, sequence, and timestamps.
- `ROOT_ITEM` stores subvolume/root metadata, embedded root inode, drop progress, UUID lineage, transaction IDs, timestamps, and reserved fields.
- `INODE_REF`, `INODE_EXTREF`, and `ROOT_REF` represent backreferences from inodes and roots.

Chunk and extent structures:
- `CHUNK_ITEM` and `CHUNK_ITEM_STRIPE` define logical chunk layout and device stripes.
- `EXTENT_DATA` and `EXTENT_DATA2` describe inline/regular/preallocated file extents.
- `EXTENT_ITEM`, `EXTENT_ITEM2`, `EXTENT_ITEM_V0`, and `EXTENT_ITEM_TREE` model extent-tree metadata records.
- `TREE_BLOCK_REF`, `EXTENT_DATA_REF`, `EXTENT_REF_V0`, `SHARED_BLOCK_REF`, and `SHARED_DATA_REF` define extent reference variants.
- `BLOCK_GROUP_ITEM` stores block group usage and flags.
- `DEV_EXTENT` maps device extents back to chunk/object metadata.

Free-space and balance structures:
- `FREE_SPACE_ENTRY`, `FREE_SPACE_ITEM`, and `FREE_SPACE_INFO` describe free-space tree/cache records.
- `BALANCE_ARGS` and `BALANCE_ITEM` describe persisted balance filters, limits, profile conversions, and per-class balance state.

Send-stream structures:
- `btrfs_send_header`, `btrfs_send_command`, and `btrfs_send_tlv` define the stream framing.
- `BTRFS_SEND_CMD_*` and `BTRFS_SEND_TLV_*` enumerate commands and attributes for send operations.

## Integration Points

`btrfs.c` uses this header for superblock probing, checksum validation, feature gating, root/chunk/device loading, free-space protection, device stats, file attributes, default subvolume lookup, and mount setup.

Other driver modules depend on these definitions for tree operations, extent-tree updates, flushing, reading/writing extents, checksums, balance, scrub, send, compression, and FSCTL handling.

## Important Invariants And Risks

- These structures are disk ABI definitions. Field order, field width, packing, and constant values must not change unless the Btrfs on-disk format itself changes.
- The variable-length structs with trailing `name[1]` or `data[1]` require callers to validate item sizes before reading beyond the fixed prefix.
- The header uses a `static_assert` for `INODE_ITEM` size only on non-ReactOS builds; ReactOS builds rely on packing and compiler behavior without that assertion.
- Feature flag constants directly drive mount admission and readonly decisions in `btrfs.c`. Incorrect constants could cause unsupported filesystems to mount writable or supported filesystems to be rejected.
- Superblock checksum code assumes `superblock.checksum` precedes `uuid` and that hashing starts at `uuid` for `sizeof(superblock) - sizeof(checksum)`.
- Send-stream constants must match userspace/Linux Btrfs conventions for interoperability.
