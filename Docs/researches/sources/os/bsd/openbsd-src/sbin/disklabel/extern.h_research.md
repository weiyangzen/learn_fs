# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/extern.h

## Purpose
Shared declarations for the `disklabel` utility.

## Key Contents
- Defines `MEG()` and `GIG()` size macros in disk blocks.
- Defines `DISCARD` and `KEEP` actions for `mpfree()`.
- Declares display, checksum, scaling, DUID, editor, mountpoint, auto-table, and write-label routines.
- Exposes global command/editor state: disk names, fstab path, mountpoints, flags, verbosity, quiet mode, and active `struct disklabel lab`.

## Notes
This header is the link between `editor.c` and the rest of `disklabel`, especially display, write, and global option state.
