# File Research: sources/local-fs/jfsutils/tune/Makefile.am

Source Automake definition for `jfs_tune`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `sbin_PROGRAMS = jfs_tune`.
- Man page `jfs_tune.8`.
- Sources: `tune.c` and `super.c`.

Filesystem relevance: minimal source build recipe for the superblock/log-superblock tune utility.
