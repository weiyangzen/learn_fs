# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_bmap.c

This file maps logical file offsets/blocks to physical device offsets for DragonFlyBSD ext2. The implemented path is the classic ext2 direct/indirect pointer tree; the ext4 extent bmap entry point is present but stubbed.

Key responsibilities:
- Implement VOP bmap conversion from logical file offset to disk byte offset.
- Return forward and backward contiguous run sizes in bytes.
- Traverse direct and indirect block pointer arrays.
- Compute indirect-block logical block paths for allocation and mapping callers.
- Read indirect blocks through vnode buffers with explicit disk offsets.

Important functions:
- `ext2_bmap`: VOP wrapper. Converts `a_loffset` to LBN, dispatches to extent or indirect mapping, converts disk blocks to byte offsets, and scales run counts to bytes.
- `ext4_bmapext`: Extent bmap placeholder; currently returns `EINVAL`.
- `readindir`: Reads an indirect block through `getblk` and strategy I/O when not cached.
- `ext2_bmaparray`: Traverses direct and indirect pointers, returns `-1` for holes, and computes sequential run lengths using `is_sequential`.
- `ext2_getlbns`: Builds the path of indirect logical blocks and offsets required to reach a data block or metadata block.

Important interactions:
- Used by buffer-cache and allocation code, especially `ext2_balloc` and truncation.
- Uses mount geometry from `ext2_mount.h` (`MNINDIR`, `blkptrtodb`, `is_sequential`).
- Reads block pointers as little-endian on-disk `e2fs_daddr_t` values.

Notable behavior and risks:
- Extent-backed bmap is not implemented, so `IN_E4EXTENTS` files return `EINVAL` here.
- `ext2_getlbns` uses 64-bit intermediate arithmetic to avoid overflow when computing triple-indirect ranges.
