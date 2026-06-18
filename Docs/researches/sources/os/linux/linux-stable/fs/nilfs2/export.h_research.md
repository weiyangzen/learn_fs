# File Research: sources/os/linux/linux-stable/fs/nilfs2/export.h

## Summary
Declares NILFS exportfs support types and the export operations object.

## Main Contents
- `extern const struct export_operations nilfs_export_ops`.
- Packed `struct nilfs_fid` for export file handles.

## Important Details
`nilfs_fid` stores checkpoint number, inode number, generation, parent generation, and parent inode number. This lets NFS/exportfs identify objects in NILFS snapshots/checkpoints as well as normal inode space.

## Risks
The structure is packed and externally visible through file-handle encoding. Field size/order changes would affect export compatibility.
