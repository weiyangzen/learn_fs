# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/gfs2_mkfs.h

Small mkfs/grow/jadd support header.

Content:
- Includes `copyright.cf`.
- Defines copied inode ioctl constants: `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FIEMAP`.
- Defines `FS_JOURNAL_DATA_FL`.

Reason:
- Avoids duplicate symbol problems from including both Linux filesystem headers and `sys/mount.h`.

Risk notes:
- Local ioctl/flag copies must remain compatible with Linux `fs.h`.
- `FS_IOC_FIEMAP` references `struct fiemap`, so users must include the appropriate fiemap definition before use or in the same translation unit.
