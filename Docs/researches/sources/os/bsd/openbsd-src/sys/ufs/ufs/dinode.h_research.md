# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dinode.h

Read completely: 156 lines.

Defines UFS inode-number types, root inode constants, UFS1/UFS2 on-disk inode formats, short-link/device overlays, and file mode/type constants.

Core definitions:
- `ufsino_t` is a 32-bit inode number; `ROOTINO` is inode 2.
- `NXADDR`, `NDADDR`, and `NIADDR` define external, direct, and indirect address counts.
- `struct ufs1_dinode` stores mode, link count, old id/inumber union, size, 32-bit timestamps, 32-bit direct/indirect block addresses, flags, block count, generation, uid/gid, and spare fields.
- `struct ufs2_dinode` stores wider uid/gid, block size, size, block count, 64-bit timestamps, birth time, generation, kernel/user flags, external attribute blocks, 64-bit direct/indirect block addresses, and spare fields.
- Defines overlays for device numbers and short symlinks, per-format max symlink lengths, permission bits, and file type bits.

Integration and risks:
- Exact field widths and positions are on-disk ABI.
- `MAXSYMLINKLEN()` depends on mount filesystem type.
- `di_rdev` and short symlink overlays reuse block address fields, so type-specific interpretation is required.
