# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dir.h

This header defines UFS directory entry layout and directory-format compatibility macros.

Key contents:
- Defines `struct direct` with inode number, record length, type, name length, and name.
- Defines directory block size, max name length, Apple UFS directory block size, and file type values.
- Defines `IFTODT` and `DTTOIF` conversions.
- Defines record sizing and padding macros.
- Defines `UFS_OLDDIRFMT` and `UFS_NEWDIRFMT`.
- Defines `struct dirtemplate` and `struct odirtemplate` for `.`/`..` directory creation.

Important compatibility note:
- Old-format directories lack `d_type`; the macro logic compensates for byte order and old-format namelen/type overlap.
