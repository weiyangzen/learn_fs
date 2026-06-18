# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.c

Provides shared utility routines for generic `fsck` and filesystem-specific checkers.

Important behavior:
- `checkroot` records `stat("/")` for root-device comparisons.
- `setcdevname`, `cdevname`, and `hotroot` manage current device name and root-filesystem detection state.
- `pfatal`, `pwarn`, `panic`, `errexit`, and `xperror` centralize formatted diagnostics, including preen-mode prefixes and fatal “run manually” behavior.
- `rawname` maps a block device path to a raw character device path by inserting `r` after the final slash.
- `unrawname` reverses raw character device names when possible.
- `blockcheck` resolves block, character, and fstab mountpoint names into raw device names, detects hot root, and validates character devices.
- `emalloc`, `ereallocarray`, and `estrdup` are fail-fast allocation wrappers.

This file is the common device-name and error-reporting substrate shared by the dispatcher and fsck helpers.
