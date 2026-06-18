# File Research: sources/local-fs/kdave-linux/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the checksum, file extent, and inode extent-range functions implemented by `file-item.c`.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the byte offset in `struct btrfs_file_extent_item` where inline data begins.
- Computes maximum inline data size for a filesystem from `BTRFS_MAX_ITEM_SIZE()` minus the inline data header.
- Computes inline data length from a leaf item size, excluding the file extent header bytes.
- Provides pointer arithmetic helpers for inline data start and inline item size calculation.
- Declares checksum deletion, lookup, insertion, bio checksum calculation, dummy checksum allocation, and range checksum lookup APIs.
- Declares conversion from a file extent item plus B-tree path into an extent map.
- Declares inode file extent range tracking helpers and safe disk i_size update.
- Declares `btrfs_file_extent_end()` for determining the logical end of a file extent item.

Dependencies:
- Includes Linux block type and list definitions, Btrfs UAPI tree structures, `ctree.h`, and ordered-data definitions.
- Forward-declares Btrfs path, bio, root, transaction, ordered-sum, inode, extent map, and file extent structures.

Important invariants:
- Inline helper calculations must match the on-disk `struct btrfs_file_extent_item` layout.
- Inline item length is the item payload size minus `BTRFS_FILE_EXTENT_INLINE_DATA_START`; compressed inline data reports compressed size by this calculation.
- The public checksum APIs operate on logical disk bytenr ranges aligned to filesystem sectors.

Notable risks:
- Any on-disk file extent layout change must update the inline data offset helpers here and all tree-checker assumptions.
- The header exposes low-level mutation helpers used by several higher-level file operations, so callers must already satisfy transaction, path, and range-locking requirements.
