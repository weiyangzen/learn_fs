# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/valid_blk.c

## Purpose
Determines whether an inode’s `i_block[]` entries should be interpreted as block mappings.

## Main Behavior
- Only directories, regular files, and symlinks can have valid block entries.
- Fast symlinks are detected specially because their target is stored inside `i_block[]`.
- Symlinks with EA blocks use size and `i_block[1]` heuristics because `i_blocks` includes EA storage.
- Inodes with `EXT4_INLINE_DATA_FL` are treated as not having valid external block entries.

## Integration
Provides `ext2fs_inode_has_valid_blocks2(fs, inode)` and compatibility wrapper `ext2fs_inode_has_valid_blocks(inode)`.

## Risks / Notes
The symlink-with-EA case is heuristic by necessity; it distinguishes likely fast symlinks from real block-backed symlinks.
