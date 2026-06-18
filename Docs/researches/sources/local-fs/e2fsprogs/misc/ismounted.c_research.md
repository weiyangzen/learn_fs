# File Research: sources/local-fs/e2fsprogs/misc/ismounted.c

## Purpose
Provides `is_mounted`, used to decide whether a filesystem/device is currently mounted.

## Key Elements
Parses mount-table-like files with small local word parsing helpers. `check_mntent_file` opens `/proc/mounts` or `/etc/mtab`, compares requested path by literal device name, block-device `st_rdev`, or non-block `st_dev/st_ino`, and validates matching mountpoint entries to avoid stale mtab data. Includes root-device fallback for `/dev/root` style cases.

`is_mounted` checks `/proc/mounts` first on Linux, then `/etc/mtab`.

## Dependencies
Uses `setmntent`/`endmntent` when available, POSIX `stat`, mount table formats, and `fsck.h`.

## Behavior/Risks
If mount table files cannot be opened or parsed, callers receive “not mounted” behavior. Some logic is disabled for GNU/Hurd due to device stat limitations. Commented paranoia reflects historically stale `/etc/mtab` issues.
