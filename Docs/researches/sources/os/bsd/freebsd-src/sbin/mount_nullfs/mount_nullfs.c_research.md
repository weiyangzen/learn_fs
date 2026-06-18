# File Research: sources/os/bsd/freebsd-src/sbin/mount_nullfs/mount_nullfs.c

## Summary
Mount helper for nullfs loopback mounts, supporting file or directory targets.

## Main Responsibilities
- Parses `-o` key/value mount options into iovecs.
- Resolves both target and mountpoint with `realpath()`.
- Requires target to be either regular file or directory.
- Requires mountpoint and target to have the same file type.
- Builds `nmount()` iovecs for `fstype=nullfs`, `fspath`, `target`, and `errmsg`.
- Reports kernel-provided error text.

## Research Notes
This helper is stricter than generic path resolution: it validates file-vs-directory type compatibility before calling the kernel.
