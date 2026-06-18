# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/Makefile.am

Automake build definition for the `resize_reiserfs` utility.

Major responsibilities:
- Builds `resize_reiserfs` as an installed sbin program.
- Compiles `fe.c`, `resize_reiserfs.c`, `do_shrink.c`, and `resize.h`.
- Installs `resize_reiserfs.8` as the manual page.
- Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Dependencies and interactions:
- The resize utility is a thin program over the shared ReiserFS core library.
- Manual page is included in `EXTRA_DIST` for distribution packaging.

Risks and notes:
- No per-target compiler flags are set here; it inherits project-wide configuration.
