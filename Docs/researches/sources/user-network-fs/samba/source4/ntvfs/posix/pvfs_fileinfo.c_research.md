# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fileinfo.c

Purpose: converts POSIX `stat` data and PVFS share flags into DOS/NT file metadata and computes Unix permissions for new files/directories.

Important APIs and functions: `dos_mode_from_stat` maps Unix mode bits to DOS readonly/archive/system/hidden/directory attributes. `pvfs_fill_dos_info` populates `pvfs_filename.dos` timestamps, attributes, allocation size, link count, EA size, file ID, xattr-backed DOS attributes, and open-database write-time overrides. `pvfs_fileperms` derives creation mode from requested DOS attributes plus share masks and force modes.

Control flow: directories are forced to size `0` and link count `1`; default stream names are cleared for base files. Timestamps are converted to NT time and augmented with nanoseconds. `pvfs_dosattrib_load` can override simple stat-derived attributes. Unless `PVFS_RESOLVE_NO_OPENDB` is set, the file locking key is queried in the open database and a non-null ODB write time overrides stat mtime. Permission creation starts from broad read/write bits, maps DOS attributes into execute bits only when native xattrs are disabled, and then applies create/dir masks and force modes.

State and persistence: this file reads persistent stat/xattr/ODB state but mostly fills in-memory `pvfs_filename` fields. New-file modes later become persistent through create/mkdir/open operations.

Dependencies and integration points: used by PVFS resolve/info/open paths. Depends on time helpers, DOS attribute xattr loading, allocation rounding, locking-key generation, and ODB file info.

Risks: attribute mapping changes when xattrs are enabled; SMB2 EA size differs from SMB1; ODB errors are logged and returned; file ID combines device and inode. Test signals include mapped archive/system/hidden bits, readonly mode creation with and without xattrs, nanosecond timestamp precision, ODB write-time override, and directory metadata normalization.
