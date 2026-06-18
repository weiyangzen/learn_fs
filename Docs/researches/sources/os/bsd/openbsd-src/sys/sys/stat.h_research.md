# File Research: sources/os/bsd/openbsd-src/sys/sys/stat.h

File status structure, mode bits, file flags, timestamp constants, and stat-family prototypes.

This header defines public `struct stat`, including mode, device, inode, links, owner/group, rdev, atime/mtime/ctime, size, block count, block size, BSD file flags, generation, and birth time. It provides POSIX and BSD timestamp aliases, permission bits, file-type bits, `S_IS*` tests, POSIX `S_TYPEIS*` stubs, BSD permission masks, block-size constant, and owner/superuser file flags.

Kernel builds get shorthand flag masks for opaque, append-only, and immutable checks. Userland gets prototypes for chmod/stat/mknod/mkdir/fifo/umask, POSIX `*at` and nanosecond timestamp operations, and BSD chflags/isfdtype calls.

Filesystem/storage relevance: central public filesystem ABI. This is the primary structure and constant set through which VFS and filesystems expose file metadata to userland.
