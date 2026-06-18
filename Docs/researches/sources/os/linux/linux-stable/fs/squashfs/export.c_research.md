# File Research: sources/os/linux/linux-stable/fs/squashfs/export.c

## Summary
Implements NFS/exportfs support for Squashfs using the inode lookup table.

## Key APIs
- `squashfs_read_inode_lookup_table()`.
- `squashfs_export_ops`.

## Important Behavior
Normal directory operations encode inode disk locations directly in directory entries. Exportfs filehandles only carry inode numbers, so `squashfs_inode_lookup()` maps inode numbers to encoded on-disk inode locations through the compressed inode lookup table.

The lookup-table index is read at mount time. `squashfs_read_inode_lookup_table()` verifies the table size matches its table boundaries and that each compressed lookup-block pointer is monotonic and close enough to the next boundary.

`fh_to_dentry`, `fh_to_parent`, and `get_parent` obtain aliases through `squashfs_iget()`.

## Risks
Export support is only installed when the image has a lookup table. Bad table geometry disables mount rather than allowing stale or out-of-range filehandle resolution.
