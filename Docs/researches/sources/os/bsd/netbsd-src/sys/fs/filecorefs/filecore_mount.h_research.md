# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_mount.h

Read completely: 92 lines.

Defines user mount arguments for Acorn FileCore filesystems. `struct filecore_args` carries the block-device path, a compatibility export-args padding field, uid/gid ownership to expose, and FileCore mount flags.

The mount flags control access interpretation and presentation: owner-only access, all-access, forced owner read, using the mounting user’s uid/gid, and optionally including file type in names. `FILECOREMNT_BITS` provides a printable bit description.
