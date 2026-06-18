# File Research: sources/os/bsd/netbsd-src/lib/libcurses/overwrite.c

Implements destructive window copy via `overwrite`.

It delegates to `copywin` using the destination’s full rectangle and overlay mode false, so source cells overwrite destination cells regardless of blankness.
