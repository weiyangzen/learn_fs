# File Research: sources/local-fs/ocfs2-tools/fswreck/extent.c

This file creates extent tree, extent block, and extent record corruptions.

Key behavior:
- `create_file()` creates and links a regular file under a directory.
- `custom_extend_allocation()` allocates clusters and inserts them in reverse order to prevent extent coalescing and force extent-tree growth.
- `damage_extent_block()` reads a file inode and its first extent block, then corrupts extent block self block number, generation, signature, list depth, list count, or next-free record.
- `damage_extent_block_by_type()` creates a file and extends it enough to guarantee an extent block before damaging it.
- `mess_up_extent_list()` and `mess_up_extent_block()` both delegate to `damage_extent_block_by_type()`.
- `mess_up_record()` corrupts inline inode extent records:
  - invalid unwritten/refcounted flags on unsupported filesystems
  - unaligned block number
  - cluster overrun near filesystem end
  - block number in invalid range
  - overlapping extents
  - holes by moving `e_cpos`
- `mess_up_extent_record()` creates a file, allocates one cluster, then corrupts its first record.

Integration notes:
- Uses libocfs2 allocation and extent insertion APIs rather than raw bitmap writes for setup.
- Feature-gated corruptions intentionally require volumes without unwritten or refcount support.
- `EXTENT_OVERLAP` and `EXTENT_HOLE` re-read the inode after extending, but keep using the already assigned extent list pointer from the buffer.
