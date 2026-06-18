# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs.h

Read completely: 153 lines.

Top-level SGI EFS format header. It documents the Extent File System layout: 512-byte basic blocks, boot/reserved block 0, superblock at block 1, bitmap placement, cylinder groups, inode areas, data extents, direct versus indirect extent descriptors, and big-endian on-disc assumptions.

Defines basic block constants and conversions (`EFS_BB_SHFT`, `EFS_BB_SIZE`, `EFS_BB2BY`, `EFS_BY2BB`), fixed layout offsets, and the 8 GB filesystem limit derived from the 24-bit extent block number.

For kernel builds it defines `VFSTOEFS()` and debug-print plumbing. The header is mostly explanatory but establishes the invariants used by the EFS mount, inode, and extent code.
