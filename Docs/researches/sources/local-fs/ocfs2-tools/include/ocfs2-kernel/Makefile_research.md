# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/Makefile

This Makefile lists kernel-derived OCFS2 compatibility headers exported for userspace builds.

Key content:
- Installs under `ocfs2-kernel`.
- Header list includes list helpers, OCFS1 compatibility, OCFS2 filesystem/ioctl/lockid definitions, quota tree, and sparse endian type annotations.

Integration notes:
- The grouped source list only included `kernel-list.h` and `ocfs1_fs_compat.h`; this Makefile references additional headers in the same public include area.
