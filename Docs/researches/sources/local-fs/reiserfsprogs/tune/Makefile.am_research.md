# File Research: sources/local-fs/reiserfsprogs/tune/Makefile.am

Automake build definition for `reiserfstune`.

Major responsibilities:
- Builds `reiserfstune` as an installed sbin program from `tune.c` and `tune.h`.
- Installs `reiserfstune.8`.
- Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.
- Adds install hook symlinks for `tunefs.reiserfs` binary and manpage aliases.

Dependencies and interactions:
- Exposes the same executable under historical/alternate `tunefs.reiserfs` naming.
- Depends on core ReiserFS library for all filesystem manipulation.

Risks and notes:
- Symlink creation uses `$(LN_S)` without explicit replacement logic; packaging/install behavior depends on automake environment and existing files.
