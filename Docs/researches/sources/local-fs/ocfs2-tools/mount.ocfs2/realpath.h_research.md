# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.h

Single-prototype header for `myrealpath(const char *path, char *resolved_path, int m)`.

Used by `sundries.c` to canonicalize paths without relying on libc `realpath`.
