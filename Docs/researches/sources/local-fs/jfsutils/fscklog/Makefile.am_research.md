# File Research: sources/local-fs/jfsutils/fscklog/Makefile.am

Automake source template for the fsck log utility.

Key contents:
- Adds include paths for top-level `include`, `libfs`, and `fsck`.
- Links `jfs_fscklog` with `../libfs/libfs.a`.
- Declares `jfs_fscklog` as an sbin program.
- Declares `jfs_fscklog.8` as a man page and extra distribution file.
- Sources: `fscklog.c`, `display.c`, `extract.c`, `jfs_fscklog.h`.

Research notes:
- This is the authoritative concise build specification; `Makefile` and `Makefile.in` are generated from it.
