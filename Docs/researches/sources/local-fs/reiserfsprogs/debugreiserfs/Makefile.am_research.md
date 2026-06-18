# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/Makefile.am

Builds the `debugreiserfs` sbin program from:
`debugreiserfs.c`, `pack.c`, `unpack.c`, `stat.c`, `corruption.c`, `scan.c`, `recover.c`, and `debugreiserfs.h`.

Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Installs compatibility symlinks:
- `debugfs.reiserfs` -> `debugreiserfs`
- `debugfs.reiserfs.8` -> `debugreiserfs.8`

Key role: packaging/build glue for the debugging and metadata extraction tool.
