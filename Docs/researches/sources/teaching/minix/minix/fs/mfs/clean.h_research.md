# File Research: sources/teaching/minix/minix/fs/mfs/clean.h

`clean.h` defines the MFS `MARKDIRTY` macro for dirtying cached buffers. If the global `superblock` is read-only, the macro prints a diagnostic and emits a stack trace with `util_stacktrace`; otherwise it delegates to `lmfs_markdirty`.

This centralizes the "do not dirty read-only filesystems" guard for buffer writes. Inode dirtying uses a similar but separate macro in `inode.h`.
