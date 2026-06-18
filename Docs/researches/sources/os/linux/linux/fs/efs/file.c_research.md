# File Research: sources/os/linux/linux/fs/efs/file.c

Implements read-only block mapping helpers for regular file I/O.

Key behavior:
- `efs_get_block()` rejects create requests with `-EROFS`.
- Returns holes/EOF without mapping when logical block is beyond `i_blocks`.
- Maps valid logical blocks through `efs_map_block()` and `map_bh()`.
- `efs_bmap()` validates non-negative and in-range block numbers, then returns the physical block mapping.

Important interactions:
- Used by `block_read_full_folio()`, `generic_block_bmap()`, directory reads, and symlink reads.
- Enforces the filesystem’s read-only behavior at the block-mapping layer.
