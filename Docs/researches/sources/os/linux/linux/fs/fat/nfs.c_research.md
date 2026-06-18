# File Research: sources/os/linux/linux/fs/fat/nfs.c

## Purpose
Implements FAT export operations for NFS, including normal inode-number file handles and `nfs=nostale_ro` file handles based on on-disk directory-entry position.

## Main Responsibilities
- Encodes/decodes FAT-specific file handles.
- Looks up inodes by VFS inode number or by FAT `i_pos` depending on NFS mode.
- Rebuilds inodes from directory entries for nostale read-only export.
- Finds parent dentries for disconnected exported directories.
- Provides two export operation tables.

## Key Interfaces
- `fat_dget()`: finds a cached directory inode by logical start cluster.
- `fat_ilookup()` / `__fat_nfs_get_inode()`: retrieve or rebuild exported inodes.
- `fat_encode_fh_nostale()`: encodes generation and `i_pos`, optionally parent `i_pos`.
- `fat_fh_to_dentry()` / `fat_fh_to_parent()`: generic file-handle decode for stale-rw mode.
- `fat_fh_to_dentry_nostale()` / `fat_fh_to_parent_nostale()`: `i_pos`-based decode for nostale mode.
- `fat_get_parent()`: resolves parent via `..`, cache lookup, or rebuild.
- `fat_export_ops` / `fat_export_ops_nostale`: export tables selected at mount.

## Important Behavior
In `FAT_NFS_NOSTALE_RO`, file handles contain the on-disk directory-entry position instead of transient `i_ino`. If an inode is not cached, `__fat_nfs_get_inode()` reads the directory-entry block and rebuilds the inode unless the entry is free.

`fat_rebuild_parent()` reconstructs a missing parent by reading the child directory’s first cluster, extracting `.` and `..`, creating a temporary grandparent inode if needed, then scanning for the child start cluster.

## Dependencies
Relies on inode hash and directory hash maintenance from `inode.c`, directory scanning from `dir.c`, and FAT position helpers from `fat.h`.

## Research Notes
The nostale mode is forced read-only during mount in `fat_fill_super()`, which avoids handle instability from directory-entry relocation or reuse during writes.
