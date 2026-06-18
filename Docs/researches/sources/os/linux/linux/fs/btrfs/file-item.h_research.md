# File Research: sources/os/linux/linux/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the file extent, checksum, ordered-sum, extent-map conversion, and inode file-extent tracking APIs implemented by `file-item.c` or expected by nearby Btrfs code.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the offset in `struct btrfs_file_extent_item` where inline payload begins.
- Computes the maximum inline data payload for a filesystem from `BTRFS_MAX_ITEM_SIZE()` minus the inline extent header.
- Computes inline payload length from a leaf item size by subtracting `BTRFS_FILE_EXTENT_INLINE_DATA_START`.
- Provides pointer arithmetic helpers for inline payload start and inline item size calculation.
- Declares checksum deletion, read-bio checksum lookup, checksum insertion, write-bio checksum calculation, dummy ordered-sum allocation, list-style checksum lookup, and bitmap-style checksum lookup.
- Declares hole extent insertion and file extent item lookup.
- Declares conversion from a file extent item and B-tree path into a `struct extent_map`.
- Declares inode file extent range set/clear helpers and safe `disk_i_size` update.
- Declares `btrfs_file_extent_end()` for deriving the exclusive logical end of a file extent item.

Dependencies:
- Includes Linux block and list definitions, the Btrfs tree UAPI, `ctree.h`, and `ordered-data.h`.
- Forward-declares `extent_map`, Btrfs path, bio, transaction, root, ordered sum, inode, and file extent structures.

Important invariants:
- Inline layout helpers must match the on-disk `struct btrfs_file_extent_item` layout exactly.
- `btrfs_file_extent_inline_item_len()` reports compressed size for compressed inline extents because it measures stored item payload bytes.
- Public checksum APIs operate on logical disk byte ranges aligned to the filesystem sector size.
- `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` callers are responsible for passing ranges that match file extent item boundaries.

Notable risks:
- This header exposes low-level mutation helpers; callers must already satisfy the required transaction, path, inode lock, mmap lock, and extent lock contracts established by higher-level code.
- The header declares `btrfs_lookup_csums_range()`, but this file group contains no implementation in `file-item.c`; within the checked tree only the declaration was found, while `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()` are implemented here.
- Any future on-disk file extent layout change must update these helpers and all tree-checker assumptions together.
