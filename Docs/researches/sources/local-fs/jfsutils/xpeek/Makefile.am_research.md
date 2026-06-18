# File Research: sources/local-fs/jfsutils/xpeek/Makefile.am

Source Automake definition for `jfs_debugfs`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `sbin_PROGRAMS = jfs_debugfs`.
- Man page `jfs_debugfs.8`.
- Source list for the interactive debugger: alter/display/fsck callback/directory/dmap/help/iag/inode/io/super/ui/xpeek modules and `xpeek.h`.

Filesystem relevance: build recipe for the JFS inspection/debugging utility.
