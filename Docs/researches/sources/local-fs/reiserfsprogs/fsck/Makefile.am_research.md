# File Research: sources/local-fs/reiserfsprogs/fsck/Makefile.am

Builds the `reiserfsck` sbin program.

Source set includes the main driver, rebuild passes, semantic checks, lost+found handling, bitmap/objectid/tree/file helpers, superblock repair, and `fsck.h`.

Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Installs compatibility symlinks:
- `fsck.reiserfs` -> `reiserfsck`
- `fsck.reiserfs.8` -> `reiserfsck.8`

Key role: build glue for the filesystem checker/repair utility.
