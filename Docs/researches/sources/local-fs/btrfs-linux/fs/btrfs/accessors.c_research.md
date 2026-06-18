# File Research: sources/local-fs/btrfs-linux/fs/btrfs/accessors.c

Implements low-level extent-buffer field accessors used to read and write little-endian on-disk metadata fields.

Key points:
- Provides generated implementations for `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()`.
- Accessors treat metadata pointers as logical offsets inside an `extent_buffer`.
- Handles fields crossing folio/page boundaries, which matters when metadata block size exceeds page size.
- Uses `get_eb_folio_index()` and `get_eb_offset_in_folio()` to find the backing folio and offset.
- Bounds checks all access against `eb->len`; bad offsets emit `btrfs_warn()` through `report_setget_bounds()`.
- Uses unaligned little-endian helpers, including split-copy assembly for cross-folio reads and writes.
- Implements `btrfs_node_key()`, copying a node key pointer’s embedded key from an extent buffer.

Role in system:
- This is the implementation backing many inline accessors declared in `accessors.h`.
- It centralizes safe on-disk field access for Btrfs metadata buffers.
