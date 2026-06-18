# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_bmap.c

This file maps logical ext2 file blocks to physical disk blocks and implements `SEEK_DATA` support for sparse files.

Key responsibilities:
- Implement VOP bmap for classic indirect files and extent-backed files.
- Return physical block numbers plus forward/backward run lengths.
- Read indirect blocks via vnode buffers and explicit device offsets.
- Build indirect-block traversal paths for mapping, allocation, and truncation.
- Locate the next allocated data block for `SEEK_DATA`.

Important functions:
- `ext2_bmap`: VOP wrapper that chooses extent or indirect mapping and returns the underlying device buffer object.
- `ext4_bmapext`: Finds the containing/nearby extent and computes mapped block and run lengths.
- `readindir`: Reads indirect blocks through the buffer cache, strategy I/O, and RACCT accounting when enabled.
- `ext2_bmaparray`: Walks direct/indirect pointers, returns `-1` for holes, and computes sequential runs.
- `ext2_bmap_seekdata`: Scans direct and indirect mappings to advance an offset to the next allocated data block.
- `ext2_getlbns`: Computes the logical metadata-block path and offsets for indirect addressing.

Important interactions:
- Used by VM/buffer-cache paths, `ext2_balloc`, and truncation.
- Depends on `ext4_ext_find_extent`, `ext4_ext_path_free`, and classic inode block arrays.

Notable risks:
- Extent mapping depends on valid extent tree headers and path allocation from `ext2_extents.c`.
- `ext2_getlbns` uses 64-bit intermediate arithmetic for large triple-indirect ranges.
