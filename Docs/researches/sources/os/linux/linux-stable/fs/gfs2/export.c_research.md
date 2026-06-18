# File Research: sources/os/linux/linux-stable/fs/gfs2/export.c

## Purpose
Implements NFS/exportfs file handle encoding and decoding for GFS2.

## Key Interfaces
- `gfs2_encode_fh()` encodes inode and optional parent formal inode/address pairs.
- `gfs2_fh_to_dentry()` and `gfs2_fh_to_parent()` decode file handles.
- `gfs2_get_name()` scans a parent directory to recover a child name.
- `gfs2_get_parent()` resolves `..`.
- `gfs2_export_ops` exports the operation table.

## Control Flow And Behavior
Small handles store the child formal inode and block address; large handles additionally store the parent. Old handle size is accepted for compatibility. Decoding rejects zero formal inode as stale and uses `gfs2_lookup_by_inum()`. Name recovery takes the parent directory glock shared and scans entries until the child block address is found.

## Dependencies
Uses exportfs, GFS2 directory read/lookup helpers, glocks, inode lookup by inum, endian conversion, and `d_obtain_alias()`.

## Risks And Invariants
Handle length negotiation returns `FILEID_INVALID` when the caller-provided buffer is too small. Parent/name recovery requires valid directory inodes and glock protection.
