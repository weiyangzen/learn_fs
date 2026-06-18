# File Research: sources/os/bsd/netbsd-src/lib/libcurses/overlay.c

Implements non-destructive window copy via `overlay`.

It delegates to `copywin` with source offsets derived from window origins and `overlay` mode set true, meaning blank source cells should not overwrite destination content.
