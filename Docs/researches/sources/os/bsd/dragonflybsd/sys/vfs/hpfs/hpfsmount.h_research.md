# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfsmount.h

Source read: complete file, 40 lines.

Purpose: Public HPFS mount argument header.

Key definitions:
- `HPFSMNT_TABLES` signals that user-provided DOS-to-Unix and Unix-to-DOS high-byte conversion tables should be used.
- `struct hpfs_args` carries block device path, export args, owner uid/gid defaults, mode mask/default, mount flags, and two 0x80-byte conversion tables.

Integration:
- Copied in from user space by `hpfs_mount()`.
- Consumed by `hpfs_mountfs()` and `hpfs_cpinit()`.

Risks and review notes:
- Conversion tables are trusted once copied from mount arguments; invalid tables can affect lookup, readdir, and name comparisons for high-bit filenames.
