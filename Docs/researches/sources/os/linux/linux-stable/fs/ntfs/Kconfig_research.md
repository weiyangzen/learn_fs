# File Research: sources/os/linux/linux-stable/fs/ntfs/Kconfig

## Summary
Kconfig options for the legacy NTFS filesystem driver.

## Contents
Defines `NTFS_FS` as a tristate depending on NLS and iomap support, `NTFS_DEBUG` for extra checks and debug messages, and `NTFS_FS_POSIX_ACL` for Linux-only POSIX ACL support.

## Important Details
The help text identifies this as NTFS support for Windows NT/2000/XP/2003-era filesystems. Debug messages are disabled by default and can be enabled by boot/module option or `/proc/sys/fs/ntfs-debug`.

## Risks
The POSIX ACL option is explicitly Linux-only and ignored by Windows. Debug mode can add significant runtime overhead.
