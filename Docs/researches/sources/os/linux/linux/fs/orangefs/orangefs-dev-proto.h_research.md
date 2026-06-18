# File Research: sources/os/linux/linux/fs/orangefs/orangefs-dev-proto.h

Defines OrangeFS kernel/userspace device protocol operation constants and shared protocol includes.

Contents:
- Operation type constants for file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, readahead flush, mount/unmount, xattr ops, params, perf counters, cancel, fsync, fs key, readdirplus, and features.
- Feature bit `ORANGEFS_FEATURE_READAHEAD`.
- Debug string and max readdir-entry constants.
- Includes `upcall.h` and `downcall.h`, making it the central protocol ABI include.
