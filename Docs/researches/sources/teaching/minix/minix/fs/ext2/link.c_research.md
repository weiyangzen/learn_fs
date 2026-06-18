# File Research: sources/teaching/minix/minix/fs/ext2/link.c

This file implements link, unlink, rmdir, symlink read, rename, truncate, and free-space operations.

Key entry points:
- `fs_link()`: creates hard links after link-count and directory checks.
- `fs_unlink()`: dispatches unlink versus rmdir behavior.
- `fs_rdlink()`: reads normal symlinks from data blocks or fast symlinks from `i_block[]`.
- `fs_rename()`: implements cross-directory and same-directory rename, replacement, directory ancestry checks, and `..` updates.
- `fs_trunc()`: truncates or frees a byte range.
- `truncate_inode()`: changes file size and frees blocks beyond new size.

Internal helpers:
- `remove_dir()`: validates directory emptiness and removes `.`/`..`.
- `unlink_file()`: deletes a directory entry and decrements link count.
- `freesp_inode()`: zeros partial blocks and frees full blocks with `write_map(..., WMAP_FREE)`.
- `zeroblock_half()` and `zeroblock_range()` zero partial block regions.

Important behavior:
- Truncation discards preallocated blocks first.
- Fast symlinks avoid block I/O by storing target text in inode block pointer space.
- Rename protects mountpoints and prevents moving a directory into its descendant.
- Directory removal depends on `search_dir(..., IS_EMPTY)`.

Notable risks:
- Several rename paths rely on inode pointer identity and comments acknowledge possible filesystem loops.
- `fs_trunc()` uses `find_inode()` and thus only operates on active in-core inodes.
