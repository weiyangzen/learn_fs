# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/Makefile

Read completely: 7 lines.

Kernel include-install Makefile for LFS public headers.

Behavior:
- Sets `INCSDIR` to `/usr/include/ufs/lfs`.
- Installs `lfs.h`, `lfs_accessors.h`, `lfs_inode.h`, and `lfs_extern.h`.
- Includes `<bsd.kinc.mk>` for NetBSD kernel include installation mechanics.

Risks and notes:
- Any header omitted here will not be installed for consumers expecting public LFS definitions.
