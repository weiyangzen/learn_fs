# File Research: sources/local-fs/jfsutils/mkfs/Makefile.in

Generated Automake 1.11.1 template for the `mkfs` directory.

Key build details:
- Builds `jfs_mkfs$(EXEEXT)` from `initmap`, `inodemap`, `inodes`, and `mkfs` objects.
- Uses Autoconf substitutions for compiler/tool paths and dependency tracking.
- Includes `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- Links `../libfs/libfs.a -luuid`.
- Installs `jfs_mkfs.8`.
- Includes install hooks to create `mkfs.jfs` binary and man-page aliases, plus uninstall cleanup.

Filesystem relevance: portable build template for the formatter source files.
