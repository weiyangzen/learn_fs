# File Research: sources/os/linux/linux-stable/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the file extent, checksum, ordered-sum, extent-map conversion, and inode file-extent tracking APIs implemented by `file-item.c` or consumed by nearby Btrfs code.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the offset where inline file extent payload begins.
- Computes maximum inline payload size from `BTRFS_MAX_ITEM_SIZE()` minus the inline extent header.
- Computes inline payload length from a leaf item size.
- Provides pointer/size helpers for inline file extent payloads.
- Declares checksum deletion, read-bio checksum lookup, checksum insertion, write-bio checksum calculation, dummy ordered-sum allocation, list checksum lookup, and bitmap checksum lookup.
- Declares explicit hole extent insertion and file extent item lookup.
- Declares conversion from a file extent item and B-tree path into `struct extent_map`.
- Declares inode file extent range set/clear helpers and safe `disk_i_size` update.
- Declares `btrfs_file_extent_end()`.

Dependencies and invariants:
- Includes Linux block/list definitions, Btrfs tree UAPI, `ctree.h`, and `ordered-data.h`.
- Forward-declares extent map, path, bio, transaction, root, ordered sum, inode, and file extent structures.
- Inline layout helpers must match the on-disk `struct btrfs_file_extent_item` layout exactly.
- `btrfs_file_extent_inline_item_len()` reports stored payload bytes, which are compressed size for compressed inline extents.
- Public checksum APIs operate on filesystem-sector-aligned logical ranges.
- File extent range tracking callers must pass ranges matching file extent item boundaries.

Notable risks:
- This header exposes low-level mutation helpers whose correctness depends on external transaction, path, inode, mmap, and extent-lock contracts.
- It declares `btrfs_lookup_csums_range()`, but this group’s implementation file provides `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()` instead.
- Any on-disk file extent layout change must update these helpers and matching tree-checker assumptions together.
