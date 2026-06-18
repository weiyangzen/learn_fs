# File Research: sources/os/bsd/openbsd-src/sys/sys/statvfs.h

POSIX-style filesystem capacity/status ABI.

This header defines `struct statvfs` with block size, fragment size, total/free/available blocks, total/free/available file counts, filesystem id, mount flags, and maximum filename length. It defines `ST_RDONLY` and `ST_NOSUID`, plus userland prototypes for `statvfs()` and `fstatvfs()`.

Filesystem/storage relevance: direct. It is a public filesystem-capacity and mount-property reporting ABI layered over VFS/statfs-style data.
