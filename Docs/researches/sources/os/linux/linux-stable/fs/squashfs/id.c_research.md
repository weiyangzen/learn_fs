# File Research: sources/os/linux/linux-stable/fs/squashfs/id.c

## Summary
Maps compact on-disk uid/gid indices to 32-bit ids using the Squashfs id lookup table.

## Key APIs
- `squashfs_get_id()`.
- `squashfs_read_id_index_table()`.

## Important Behavior
Inodes store uid and gid table indices. `squashfs_get_id()` validates the index, reads the selected 32-bit id from compressed metadata, and returns the host-endian value.

The id index table is read at mount time. Its computed size must exactly match table boundaries, and each compressed id-block pointer must be monotonic and within one metadata block plus header slack of the next boundary.

## Risks
Every inode read depends on this table. Corrupt id geometry is treated as a mount failure, while out-of-range inode uid/gid indices fail individual inode reads.
