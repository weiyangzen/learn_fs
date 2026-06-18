# File Research: sources/local-fs/jfsutils/logdump/Makefile.am

This is the Automake source for the logdump utility build.

Contents:
- Adds include paths for top-level `include` and `libfs`.
- Links `jfs_logdump` with `../libfs/libfs.a -luuid`.
- Installs `jfs_logdump` as an sbin program.
- Distributes/installs `jfs_logdump.8`.
- Builds from `logdump.c` and `helpers.c`.

This file is the maintainable source for the generated `logdump/Makefile`.
