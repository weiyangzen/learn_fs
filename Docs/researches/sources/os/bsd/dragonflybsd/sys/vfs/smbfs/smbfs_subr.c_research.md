# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.c

This file contains SMBFS support routines for time conversion, full-path construction, and filename conversion.

The time code converts among Unix `timespec`, SMB server seconds, NT 100ns-since-1601 timestamps, and DOS date/time fields. DOS conversion logic is inherited from msdosfs-style routines and caches the last computed date/time to avoid repeated full calendar conversion.

`smbfs_fullpath` serializes an SMB path into an mbchain by walking parent links through `smb_fphelp`, adding backslash separators, applying uppercase conversion for old dialects, and appending an optional final component. The helper uses the mount’s `sm_npstack` as a temporary parent stack and enforces `SMBFS_MAXPATHCOMP`.

`smbfs_fname_tolocal` applies the VC’s local iconv conversion when available. Case conversion hooks are present but commented out.
