# File Research: sources/local-fs/jfsutils/mkfs/Makefile.am

Source Automake definition for `jfs_mkfs`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- `sbin_PROGRAMS = jfs_mkfs`.
- Man page `jfs_mkfs.8`.
- Sources: `initmap.c`, `inodemap.c`, `inodes.c`, `mkfs.c`, `initmap.h`, `inodemap.h`, `inodes.h`.

Install hooks create the standard `mkfs.jfs` command and man-page aliases. Uninstall hook removes those aliases.
