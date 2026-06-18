# File Research: sources/local-fs/jfsutils/include/Makefile

Configured Automake-generated Makefile for the `include` distribution directory.

Key contents:
- No compile targets; `SOURCES` and `DIST_SOURCES` are empty.
- `EXTRA_DIST` lists all public/shared JFS format headers:
  `jfs_byteorder.h`, `jfs_btree.h`, `jfs_dinode.h`, `jfs_dmap.h`, `jfs_dtree.h`, `jfs_filsys.h`, `jfs_imap.h`, `jfs_logmgr.h`, `jfs_superblock.h`, `jfs_types.h`, `jfs_unicode.h`, `jfs_version.h`, `jfs_xtree.h`.
- Contains configured build variables with concrete paths/version from configure output.
- Provides dist, clean, maintainer-clean, and no-op install targets.

Research notes:
- The include directory is packaged for distribution, not installed as headers by this makefile.
