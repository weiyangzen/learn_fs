# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_subr.h

Read completely: 48 lines.

Declares the EFS inode pool, extent iterator state, and helper routines implemented in `efs_subr.c`.

The iterator tracks the inode, next logical extent, next direct extent, and next indirect extent index. Prototypes cover superblock checksum/validation, inode location/read, extent conversion, directory lookup, block reads, inode sync conversion, and extent iterator initialization/advance.
