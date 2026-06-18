# File Research: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.c

## Purpose
Provides structured, endian-aware printing for common on-disk GFS2 metadata structures.

## Main Elements
- `print_it()` formats label/value output for curses or stdout, handles highlighting, edit field capture, and decimal/hex secondary display.
- Print macros convert big-endian 16/32/64-bit fields and 8-bit fields.
- Structure printers: inum, meta header, superblock, rindex, rgrp, quota, dinode, leaf, eattr header, log header, log descriptor, statfs change, and quota change.
- `ea_header_print()` bounds-checks and prints extended attribute names.

## Dependencies And Integration
Used by `gfs2hex.c`, `extended.c`, and restore print mode to render typed structures. Depends on global cursor/display state from `hexedit.h`.

## Risk Notes
Uses fixed buffers and `vsprintf()`. Highlight/edit metadata is tied to global line and mode state, so changes to display layout can affect editing behavior.
