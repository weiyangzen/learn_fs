# File Research: sources/local-fs/ocfs2-tools/libocfs2/inode.c

Implements core OCFS2 userspace inode I/O and endian conversion.

Key behavior:
- `ocfs2_check_directory()` validates an inode block number, reads the inode, and checks `S_ISDIR(i_mode)`.
- `ocfs2_read_inode()` reads one filesystem block, checks `OCFS2_INODE_SIGNATURE`, validates metadata ECC via `ocfs2_validate_meta_ecc()`, copies the block to the caller, and swaps it to CPU endian.
- `ocfs2_write_inode()` requires `OCFS2_FLAG_RW`, swaps a caller-provided CPU-endian inode to disk endian, recomputes metadata ECC, writes the block, and marks the fs changed.
- `ocfs2_write_inode_without_meta_ecc()` is the same write path without recomputing ECC, explicitly for corruption-injection use by fswreck.

Endian handling:
- The swap path is staged because `ocfs2_dinode` contains unions whose active interpretation depends on flags and mode.
- `ocfs2_swap_inode_first()` swaps common inode fields.
- `ocfs2_swap_inode_second()` swaps device, bitmap, journal, superblock, local alloc, chain, dealloc, inline-data, or indexed-directory union members.
- `ocfs2_swap_inode_third()` swaps chain records or truncate-log records after header counts are in CPU order.
- `has_extents()` excludes super/local-alloc/chain/dealloc inodes, fast symlinks, and inline-data inodes from extent-list swapping.
- Inline directory data is swapped through directory-entry swap helpers, clamped by `ocfs2_max_inline_data_with_xattr()` so corrupt xattr sizes do not overrun the inline area.

Dependencies and interactions:
- Uses block allocation wrappers from `memory.c`.
- Uses metadata ECC helpers, extent-list swap helpers, xattr swap helpers, directory-entry swap helpers, and low-level `ocfs2_read_blocks()` / `io_write_block()`.
- The file is foundational: higher-level path lookup, quota, journal, refcount, and open-super paths all rely on its validated inode read/write semantics.

Important invariants:
- Valid block numbers are between `OCFS2_SUPER_BLOCK_BLKNO` and `fs->fs_blocks`.
- Caller-facing inode buffers are CPU-endian after read and expected CPU-endian before write.
- Signature validation happens before copying/swapping; ECC validation happens on the raw on-disk block before caller use.
