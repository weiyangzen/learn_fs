# File Research: sources/local-fs/gfs2-utils/gfs2/Makefile.am

## Purpose
Recursive Automake entry point for the `gfs2` utilities tree.

## Main Elements
- `MAINTAINERCLEANFILES = Makefile.in`.
- `SUBDIRS`: `include`, `libgfs2`, `edit`, `fsck`, `mkfs`, `man`, `tune`, `glocktop`, and `scripts`.

## Dependencies And Integration
Defines build order for shared headers/library before tools such as `gfs2_edit` and `fsck.gfs2`.

## Risk Notes
Subdirectory order matters because utility targets link against `gfs2/libgfs2/libgfs2.la`.
