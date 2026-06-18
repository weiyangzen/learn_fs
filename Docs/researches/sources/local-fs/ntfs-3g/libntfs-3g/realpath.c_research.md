# File Research: sources/local-fs/ntfs-3g/libntfs-3g/realpath.c

## Purpose
Provides device-path canonicalization, with Linux-specific repair for device-mapper paths.

## Main Interfaces
- `ntfs_realpath()` fallback is provided only when system `realpath()` is unavailable.
- `ntfs_realpath_canonicalize()` canonicalizes a path and maps `/dev/dm-N` back to `/dev/mapper/<name>` on Linux.
- Internal `canonicalize_dm_name()` reads `/sys/block/<dm>/dm/name`.

## Control Flow
Canonicalization first resolves the path normally. On Linux, if the basename matches `dm-<digits>`, it reads the device-mapper name from sysfs and returns `/dev/mapper/<name>` instead.

## Integration Points
Used around mount/device path reporting to avoid canonicalizing mapper devices into paths that are difficult to unmount.

## Risks
The fallback `ntfs_realpath()` copies into `PATH_MAX` bytes but writes `resolved_path[PATH_MAX]`, so callers must provide at least `PATH_MAX + 1` bytes. Linux mapper repair depends on sysfs availability.
