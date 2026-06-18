# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_error.c

## Purpose
Implements XFS error reporting, corruption reporting, verifier diagnostics, inode verifier diagnostics, and debug-only error injection tags.

## Debug Error Injection
Under `DEBUG`, errortags are exposed through a per-mount `errortag` sysfs kobject. Users can set random factors by tag name/id, restore defaults, copy active tags between mounts, clear all tags, test random injection, or inject millisecond delays. Removed injection types such as dropped writes are rejected.

## Reporting APIs
- `xfs_error_report` emits internal error alerts and stack traces according to `xfs_error_level`.
- `xfs_corruption_error` optionally hex-dumps corrupted buffers, reports the internal error, and tells the user to run repair.
- `xfs_buf_corruption_error` reports relationship/semantic buffer corruption outside verifier paths.
- `xfs_buf_verifier_error` records buffer I/O error state and reports CRC versus corruption failures, with optional first-128-byte dump and stack trace.
- `xfs_verifier_error` is a convenience wrapper for whole-buffer verifier failures.
- `xfs_inode_verifier_error` reports inode metadata CRC/corruption diagnostics.

## Dependencies
Uses XFS sysfs helpers, alert/warn logging, panic tags, random numbers, delay primitives, stack trace/hex dump helpers, buffer I/O error marking, and inode/buffer metadata context.
