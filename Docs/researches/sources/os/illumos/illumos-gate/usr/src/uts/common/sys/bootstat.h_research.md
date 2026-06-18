# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootstat.h

This header defines booter-neutral file metadata structures usable by ILP32 and LP64 boot code. `boottime_t` uses explicit 64-bit seconds/nanoseconds, and `struct bootstat` mirrors the subset of `stat` fields needed by booters, including mode, inode, size, times, block fields, and filesystem type.

`struct compinfo` carries pre-root compressed-file metadata for `kobj`, before later filesystem-level decompression takes over.
