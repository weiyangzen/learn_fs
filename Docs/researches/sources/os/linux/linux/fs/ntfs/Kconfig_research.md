# File Research: sources/os/linux/linux/fs/ntfs/Kconfig

## Role

This Kconfig file defines build options for the legacy Linux NTFS filesystem driver.

## Options

`NTFS_FS` is a tristate option that selects `NLS` and `FS_IOMAP`. It builds as module `ntfs` when selected as `M`.

`NTFS_DEBUG` depends on `NTFS_FS` and enables additional consistency checks and debug messages. The help warns that enabled debug messages can significantly slow the system.

`NTFS_FS_POSIX_ACL` depends on `NTFS_FS`, selects `FS_POSIX_ACL`, and enables Linux-only POSIX ACL support for NTFS, with the note that Windows ignores these ACLs.

## Design Notes

The driver now depends on iomap infrastructure, and ACL support is explicit rather than implied by core NTFS support.
