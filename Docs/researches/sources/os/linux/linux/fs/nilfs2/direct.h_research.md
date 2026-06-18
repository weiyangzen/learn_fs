# File Research: sources/os/linux/linux/fs/nilfs2/direct.h

This header defines the direct block-pointer bmap constants and exported direct-map entry points.

Key contents:
- `NILFS_DIRECT_NBLOCKS`: number of inline direct block pointers available in a bmap.
- `NILFS_DIRECT_KEY_MIN` and `NILFS_DIRECT_KEY_MAX`: direct mapping key range.
- Declares:
  - `nilfs_direct_init()`
  - `nilfs_direct_delete_and_convert()`

Important role:
- Direct maps are the compact mapping format for small files or metadata maps.
- `nilfs_direct_delete_and_convert()` is part of direct/B-tree format transition logic.
