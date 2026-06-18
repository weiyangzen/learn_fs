# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfsmount.h

This header defines NTFS mount flags and the user-kernel mount argument structure. Flags include case-insensitive lookup, showing all name variants, and using kernel iconv conversion.

`struct ntfs_args` carries the block device path, export args, default uid/gid/mode, flags, a 256-entry Unix-to-wchar table, and local/NTFS charset names for iconv.

Research notes: NTFS permission and charset behavior is mount-option driven rather than read from NTFS ACLs.
