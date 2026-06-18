# File Research: sources/os/linux/linux/fs/efs/Kconfig

Defines the `EFS_FS` build option.

Key behavior:
- Adds tristate support for the SGI IRIX EFS filesystem.
- Depends on `BLOCK` and selects `BUFFER_HEAD`.
- Documents the implementation as read-only.
- Module name is `efs`.

Important interactions:
- EFS support is for legacy SGI media and partitions.
