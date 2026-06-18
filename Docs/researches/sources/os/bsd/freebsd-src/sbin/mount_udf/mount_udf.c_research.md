# File Research: sources/os/bsd/freebsd-src/sbin/mount_udf/mount_udf.c

## Summary
Mount helper for UDF filesystems with optional charset conversion.

## Main Responsibilities
- Parses standard mount options, verbose flag, and `-C charset`.
- Loads `udf_iconv` and registers Unicode-to-local charset conversion when requested.
- Resolves mountpoint, normalizes source device path, and forces read-only mounting.
- Builds `nmount()` iovecs for `fstype=udf`, `fspath`, `from`, UDF flags, and optional charset names.

## Research Notes
The helper states UDF filesystems are not writable and always sets `MNT_RDONLY`.
