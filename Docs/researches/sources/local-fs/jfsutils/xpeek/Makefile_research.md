# File Research: sources/local-fs/jfsutils/xpeek/Makefile

Configured Automake-generated makefile for `jfs_debugfs`, the interactive JFS debug/inspection tool.

Key build details:
- Builds `jfs_debugfs$(EXEEXT)`.
- Sources include `alter.c`, `display.c`, `fsckcbbl.c`, `iag.c`, `io.c`, `super2.c`, `xpeek.c`, `directory.c`, `dmap.c`, `help.c`, `inode.c`, `super.c`, `ui.c`, and `xpeek.h`.
- Links `../libfs/libfs.a -luuid`.
- Installs `jfs_debugfs.8`.
- Contains concrete configured values for the local build, including `/data2/jfsutils-1.1.15` paths and `host_alias=mipsel-buildroot-linux-uclibc-`.

Filesystem relevance: configured build metadata for the JFS low-level debug browser/editor.
