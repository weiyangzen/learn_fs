# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-dev-proto.h

## Scope

This header defines operation codes and constants shared by the OrangeFS kernel module and userspace client device protocol.

## APIs And Constants

- Defines `ORANGEFS_VFS_OP_*` operation types for file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, mount/unmount, xattrs, params, perf counts, cancel, fsync, fskey, readdirplus, and features.
- Defines `ORANGEFS_FEATURE_READAHEAD`.
- Defines `ORANGEFS_MAX_DEBUG_STRING_LEN` and `ORANGEFS_MAX_DIRENT_COUNT_READDIR`.
- Includes both upcall and downcall protocol headers.

## Risks And Invariants

- Constants are userspace ABI and must stay 32/64-bit clean.
- Comments require miscellaneous constants to remain multiples of 8 for mixed-width compatibility.
