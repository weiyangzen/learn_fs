# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.h

This header defines Fossil/Vac metadata structures and constants used by `vac.c` and viewers: `DirEntry`, `MetaEntry`, `MetaBlock`, metadata magic/header/index sizes, directory entry magic, mode bits, and optional directory-entry field tags.

It declares pack/unpack, allocation, search, insert/delete, resize, cleanup, and copy routines for directory metadata.

The mode-bit enum combines Plan 9 style permissions and flags with extra DOS-like flags and snapshot semantics.
