# File Research: sources/teaching/xv6-riscv/kernel/file.h

Defines core file-layer structures.

Contents:
- `struct file` represents an open file descriptor target with type, refcount, readability/writability, pipe pointer, inode pointer, offset, and device major number.
- Device-number macros: `major`, `minor`, `mkdev`.
- `struct inode` is the in-memory inode cache entry, with refcount, sleeplock, validity flag, copied disk inode fields, and block addresses.
- `struct devsw` maps major device numbers to read/write functions.
- `CONSOLE` is major device 1.

Filesystem relevance: this header defines the in-memory shape used by both the file table and inode cache. `struct inode` is the primary object shared by `fs.c`, `file.c`, `sysfile.c`, and `exec.c`.
