# File Research: sources/os/linux/linux-stable/fs/fat/nfs.c

This file implements NFS export support for FAT, including a normal stale-capable mode and a read-only no-stale mode based on stable directory-entry positions.

Key responsibilities:
- Encode and decode FAT file handles.
- Reconstruct inodes from either VFS inode numbers or FAT directory-entry positions.
- Find parent directories for disconnected dentries.
- Support a special `nfs=nostale_ro` mode that forces read-only export and uses `i_pos`-based handles.

Important data:
- `struct fat_fid` stores generation, child `i_pos`, and optional parent `i_pos` plus parent generation.
- `FAT_FID_SIZE_WITHOUT_PARENT` and `FAT_FID_SIZE_WITH_PARENT` define file-handle lengths.

Important functions:
- `fat_dget()` finds a cached directory inode by logical start cluster through `dir_hashtable`.
- `fat_ilookup()` chooses `fat_iget(i_pos)` in no-stale mode or normal `ilookup()` in stale-capable mode.
- `__fat_nfs_get_inode()` validates generation and, in no-stale mode, can read the directory-entry block and rebuild an inode if the entry is not free.
- `fat_encode_fh_nostale()` encodes child and optional parent directory-entry positions into the file handle.
- `fat_fh_to_dentry()` and `fat_fh_to_parent()` delegate normal handles to generic export helpers.
- `fat_fh_to_dentry_nostale()` and `fat_fh_to_parent_nostale()` decode `fat_fid` and obtain aliases from rebuilt inodes.
- `fat_rebuild_parent()` reconstructs a parent by reading a child directory’s `.` and `..` entries, using a cached or dummy grandparent to scan for the matching cluster.
- `fat_get_parent()` reads `..`, tries `fat_dget()`, and falls back to parent rebuild in no-stale mode.

Export operations:
- `fat_export_ops` uses generic inode-number file handles and can become stale after FAT rename/delete behavior.
- `fat_export_ops_nostale` uses custom `i_pos` handles and parent reconstruction, intended for read-only export.

Failure behavior:
- File handles with insufficient length or unknown type return `NULL`.
- If a no-stale decoded directory entry is free, no inode is built.
- Parent reconstruction depends on readable directory clusters and may fail if required cached/dummy traversal cannot be constructed.

Research relevance:
- This file explains the FAT NFS tradeoff: normal exports are simpler but can go stale, while no-stale exports use on-disk directory positions and are restricted to read-only mounts.
