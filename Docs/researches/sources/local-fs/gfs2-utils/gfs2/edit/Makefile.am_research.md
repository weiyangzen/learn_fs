# File Research: sources/local-fs/gfs2-utils/gfs2/edit/Makefile.am

## Purpose
Builds the `gfs2_edit` administrative/editor utility.

## Main Elements
- Installs `gfs2_edit` under `sbin_PROGRAMS`.
- Headers: `gfs2hex.h`, `hexedit.h`, `extended.h`, `struct_print.h`, `journal.h`.
- Sources: `gfs2hex.c`, `hexedit.c`, `savemeta.c`, `extended.c`, `struct_print.c`, `journal.c`.
- Links against `libgfs2`, ncurses, zlib, bzip2, and uuid.
- Includes `checks.am` when Check is available.

## Dependencies And Integration
Uses global `AM_CPPFLAGS` and configured dependency flags from `configure.ac`. The executable depends on libgfs2 metadata parsing, curses display, and compression libraries for save/restore metadata.

## Risk Notes
The unit test target compiles the whole tool with `-DUNITTESTS`; this avoids the real `main()` but still pulls in broad operational code.
