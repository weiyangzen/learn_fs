# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_subr.h

This header declares SMBFS utility types, directory-search state, debug macros, lock command constants, and the SMB wire helper API.

`struct smbfattr` is the filesystem-neutral attribute structure populated from SMB replies: DOS attributes, size, access/change/modify times, and pseudo inode. `struct smbfs_fctx` tracks findfirst/findnext/findclose operations, including flags, current result attributes/name, wildcard, directory node, SMB credential, request state, remaining entries, search key, SMB search ID, info level, and resume-name data.

The function declarations cover byte-range locks, statfs variants, file-size changes, path/handle attribute updates, opens/closes, create/delete/rename/move/mkdir/rmdir, directory enumeration, full path construction, filename conversion, and all time conversion helpers.
