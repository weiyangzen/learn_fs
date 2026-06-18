# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_smb.c

## Purpose

Implements SMB1 wire-level filesystem operations for SMBFS: locks, statfs, file size/attrs/times, open/close/create/delete/rename/move/mkdir/rmdir, directory search, and lookup.

## Main Entry Points

Identity and locking:
- `smbfs_getino()` synthesizes inode numbers from parent inode plus filename hash.
- `smbfs_smb_lock()` uses `SMB_COM_LOCKING_ANDX` for LANMAN1+ dialects.

Filesystem stats:
- `smbfs_smb_statfs()` tries TRANS2 size info, then allocation info, then legacy disk info.

Size/flush:
- `smbfs_smb_seteof()` sends TRANS2 set end-of-file.
- `smbfs_smb_setfsize()` tries EOF info first, then falls back to legacy zero-length write at the requested offset.
- `smbfs_smb_flush()` sends `SMB_COM_FLUSH` only when `NFLUSHWIRE` is set.

Attributes/times:
- `smbfs_smb_query_info()` sends `SMB_COM_QUERY_INFORMATION`.
- `smbfs_smb_setpattr()`, `smbfs_smb_setptime2()`, `smbfs_smb_setpattrNT()`, `smbfs_smb_setftime()`, and `smbfs_smb_setfattrNT()` cover legacy, TRANS2, and NT basic-info variants.

Namespace and file operations:
- `smbfs_smb_open()` sends `SMB_COM_OPEN` and records fid/granted mode.
- `smbfs_smb_close()` sends `SMB_COM_CLOSE`.
- `smbfs_smb_create()` creates and immediately closes a file.
- `smbfs_smb_delete()`, `smbfs_smb_rename()`, `smbfs_smb_move()`, `smbfs_smb_mkdir()`, and `smbfs_smb_rmdir()` build path-based SMB requests.

Directory search:
- Legacy `SMB_COM_SEARCH` path: `smbfs_smb_search()`, `smbfs_findopenLM1()`, `smbfs_findnextLM1()`, `smbfs_findcloseLM1()`.
- TRANS2 path: `smbfs_smb_trans2find2()`, `smbfs_findopenLM2()`, `smbfs_findnextLM2()`, `smbfs_findcloseLM2()`.
- Public wrappers `smbfs_findopen()`, `smbfs_findnext()`, and `smbfs_findclose()` choose dialect-specific behavior, skip `.`/`..`, convert filenames to local encoding, and assign pseudo inode numbers.

Lookup:
- `smbfs_smb_lookup()` handles root specially, otherwise runs a single-entry directory search and returns attributes.

## Integration Points

This file is used by SMBFS VOP, I/O, node, and VFS operations. It depends heavily on `netsmb` request builders (`smb_rq`, `smb_t2rq`, `mbchain`, `mdchain`) and utility functions from `smbfs_subr.c`.

## Risks and Review Notes

The implementation is SMB1 dialect-dependent and includes legacy fallbacks for old servers. Unicode directory names, resume-name handling, and dialect-specific info levels are the highest-risk compatibility areas.

Several operations depend on old commands such as `SMB_COM_OPEN`, `SMB_COM_CREATE`, and `SMB_COM_SEARCH`; modern SMB behavior is outside this file’s protocol model.
