# File Research: sources/local-fs/reiserfsprogs/include/io.h

Declares the user-space buffer-cache interface used by reiserfsprogs. `struct buffer_head` mirrors kernel-style buffer metadata: block number, device fd, size, data pointer, state bits, refcount, callback hooks, list links, and hash links.

Defines buffer state flags and macros for dirty, uptodate, locked, clean, and do-not-flush status. Exposes `getblk()`, `bread()`, `bwrite()`, `brelse()`, `bforget()`, buffer lookup, flush/free/invalidate operations, and fsck rollback-file helpers.
