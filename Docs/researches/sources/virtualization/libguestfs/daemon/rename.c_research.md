# File Research: sources/virtualization/libguestfs/daemon/rename.c

Simple rename syscall wrapper.

Important behavior:
- `do_rename(oldpath, newpath)` calls `rename` under chroot.
- Reports both source and destination on error.

Filesystem relevance: atomic guest path rename where supported by the underlying filesystem.
