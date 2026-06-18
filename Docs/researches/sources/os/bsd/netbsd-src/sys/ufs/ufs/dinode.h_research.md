# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dinode.h

This header defines UFS on-disk inode formats and file mode constants.

Key contents:
- Defines `UFS_ROOTINO` as inode 2 and `UFS_WINO` as whiteout inode 1.
- Defines direct/indirect pointer counts: `UFS_NDADDR`, `UFS_NIADDR`, and UFS2 external attribute pointer count `UFS_NXADDR`.
- Defines `struct ufs1_dinode` and `struct ufs2_dinode`.
- Defines short symlink capacity for UFS1 and UFS2.
- Defines file permission and file type mode constants.
- Defines on-disk inode sizes.

Important distinction:
- UFS1 stores 32-bit block pointers and older uid/gid compatibility fields.
- UFS2 stores 64-bit block pointers, birthtime, external attribute block metadata, and larger block accounting.
