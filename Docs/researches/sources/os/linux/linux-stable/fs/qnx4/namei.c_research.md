# File Research: sources/os/linux/linux-stable/fs/qnx4/namei.c

## Summary
Implements QNX4 directory lookup.

## Main Responsibilities
- Scan directory blocks for an entry whose name matches a dentry.
- Handle normal inode entries and link entries.
- Resolve matched inode numbers through `qnx4_iget()`.
- Return aliases through `d_splice_alias()`.

## Key Interfaces
- `qnx4_lookup()` is the exported directory lookup operation.
- `qnx4_find_entry()` scans directory contents.
- `qnx4_match()` validates and compares one directory entry.

## Important Behavior
QNX4 can write placeholder entries with all options zero; `get_entry_fname()` filters invalid/unused entries so lookup does not match them. Link entries replace the initially calculated inode number with the linked inode block/index.

## Cross-File Interactions
Uses `qnx4_block_map()` and `qnx4_iget()` from `inode.c`, and directory entry helpers from `qnx4.h`.
