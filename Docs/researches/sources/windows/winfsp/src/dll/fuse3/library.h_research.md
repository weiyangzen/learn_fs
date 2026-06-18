# File Research: sources/windows/winfsp/src/dll/fuse3/library.h

This is the internal header for the FUSE3 compatibility layer.

Key contents:
- Includes the FUSE2 internal header, then undefines FUSE2 include/version/main guards before including `fuse3/fuse.h`.
- Defines `struct fuse3` with copied args, FUSE3 operations, user data, and a backpointer to the adapted FUSE2 `struct fuse`.

Filesystem relevance:
- Keeps FUSE2 and FUSE3 headers coexisting in one translation unit.
- Defines the bridge object used by `fuse2to3.c` and `fuse3.c`.
