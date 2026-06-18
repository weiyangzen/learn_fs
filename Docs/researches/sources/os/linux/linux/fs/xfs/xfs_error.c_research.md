# File Research: sources/os/linux/linux/fs/xfs/xfs_error.c

Implements XFS error reporting, corruption reporting, verifier diagnostics, and debug-only error injection sysfs controls.

Key behavior:
- Under DEBUG, builds errortag default probability/delay tables and sysfs attributes from `xfs_errortag.h`.
- Supports setting errortags by numeric tag or name, copying tags between mounts, and clearing all tags.
- `xfs_errortag_test` randomly injects tagged errors based on configured frequency; `xfs_errortag_delay` injects millisecond delays.
- `xfs_error_report` logs internal errors and stack traces according to `xfs_error_level`.
- `xfs_corruption_error` can hex-dump corrupt buffers and instructs users to unmount and run repair.
- Buffer, generic verifier, and inode verifier reporting functions distinguish CRC from structural corruption, set buffer I/O error state where appropriate, dump initial corrupt bytes based on error level, and optionally stack trace.

This file centralizes XFS diagnostic policy and debug fault injection hooks.
