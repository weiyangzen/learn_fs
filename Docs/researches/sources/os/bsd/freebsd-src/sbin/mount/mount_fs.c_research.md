# File Research: sources/os/bsd/freebsd-src/sbin/mount/mount_fs.c

## Summary
Implements direct `nmount()` mounting for filesystems that do not require an external `mount_*` helper.

## Main Responsibilities
- Parses per-mount `-o` options.
- Converts standard mount options to `mntflags` with `getmntopts`.
- Adds each option as an iovec key/value pair.
- Validates and canonicalizes the mount path with `checkpath`.
- Normalizes the source path with `rmslashes`.
- Builds required iovecs: `fstype`, `fspath`, `from`, and `errmsg`.
- Calls `nmount()` and reports kernel-provided error text.

## Dependencies And Integration
Called by `mountfs()` in `mount.c`. Uses `build_iovec`, `getmntopts`, and FreeBSD `nmount()`.
