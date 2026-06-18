# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_smb.c

This file implements SMB protocol operations used by the SMBFS vnode and VFS layers. It constructs SMB_COM and TRANS2 requests, parses replies, maps SMB metadata into `smbfattr`, and provides directory enumeration across dialect variants.

It generates pseudo inode numbers with parent inode plus `smbfs_hash`, with optional MD5 support compiled out unless `USE_MD5_HASH` is enabled. Locking is implemented via `SMB_COM_LOCKING_ANDX` for LANMAN1+ dialects.

Filesystem statistics are fetched through either TRANS2 `QUERY_FS_INFORMATION` (`smbfs_smb_statfs2`) or legacy `QUERY_INFORMATION_DISK` (`smbfs_smb_statfs`). File size, path attributes, handle timestamps, NT basic info, opens, closes, creates, deletes, renames, moves, mkdir, and rmdir are each represented by dedicated helpers.

Directory search has two implementations. Older dialects use `SMB_COM_SEARCH` with fixed 8.3-style entries and search keys. LANMAN2/NT dialects use TRANS2 `FIND_FIRST2`/`FIND_NEXT2`, support long names, resume names, server search IDs, and NT time/attribute formats. `smbfs_findopen`, `smbfs_findnext`, and `smbfs_findclose` abstract those dialect differences.

`smbfs_smb_lookup` is built on the directory search machinery. It has explicit handling for root and dot lookups, weak handling for `..`, and returns attributes plus pseudo inode values. Name conversion to local encoding is performed after directory entries are read.
