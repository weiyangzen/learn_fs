# File Research: sources/os/linux/linux-stable/fs/squashfs/namei.c

## Summary
Implements filename lookup in Squashfs directories.

## Key APIs
- `squashfs_dir_inode_ops`.

## Important Behavior
Directories are sorted and organized as headers plus entries sharing a common inode start block. Long directories can have an index that maps names to metadata blocks. `get_dir_index_using_name()` scans that index to find the first indexed name greater than the target and starts the main lookup near that block.

`squashfs_lookup()` validates name length, reads directory headers and entries, stops early when the first character has passed the target in sorted order, and calls `squashfs_iget()` for a matching entry. The inode identifier combines the header start block with the entry offset; the displayed inode number combines the header base with the signed entry delta.

## Risks
The directory index is an optimization and lookup continues if index reading fails. Sorted-order early exit depends on valid image ordering; malformed images are primarily caught by size/count validation and read failures.
