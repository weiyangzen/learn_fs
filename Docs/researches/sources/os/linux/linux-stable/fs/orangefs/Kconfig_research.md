# File Research: sources/os/linux/linux-stable/fs/orangefs/Kconfig

## Scope

This Kconfig entry exposes OrangeFS client filesystem support.

## Configuration Behavior

- Defines `ORANGEFS_FS` as a tristate option labeled `ORANGEFS (Powered by PVFS) support`.
- Selects `FS_POSIX_ACL`.

## Dependencies And Role

- The help text identifies OrangeFS as a parallel filesystem for high-end computing systems.
- POSIX ACL support is always selected when the filesystem is enabled.
