# File Research: sources/os/linux/linux-stable/fs/qnx4/dir.c

## Summary
Implements QNX4 directory iteration and directory file/inode operations.

## Main Responsibilities
- Walk directory file blocks through `qnx4_block_map()`.
- Interpret each directory entry as either an inode entry or link entry.
- Emit valid names with `dir_emit()`.
- Provide `qnx4_dir_operations` and `qnx4_dir_inode_operations`.

## Key Interfaces
- `qnx4_readdir()` is the `iterate_shared` implementation.
- `qnx4_dir_operations` uses generic llseek/read-dir/fsync/lease helpers.
- `qnx4_dir_inode_operations.lookup` points to `qnx4_lookup()`.

## Important Behavior
QNX4 link entries redirect inode calculation through `dl_inode_blk` and `dl_inode_ndx`; non-link entries calculate inode numbers from the containing block and entry index. Name validation is delegated to `get_entry_fname()`.

## Cross-File Interactions
Uses directory entry helpers from `qnx4.h`, block mapping from `inode.c`, and lookup from `namei.c`.
