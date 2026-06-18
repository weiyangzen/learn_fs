# File Research: sources/os/linux/linux-stable/fs/efs/Kconfig

## Summary
Declares SGI EFS filesystem support.

## Main Contents
- `CONFIG_EFS_FS`
- Depends on `BLOCK`
- Selects `BUFFER_HEAD`
- Described as read-only support for older SGI IRIX EFS media.

## Important Behavior
The help text explicitly states this implementation only offers read-only access.

## Risks
None in logic; enabling it adds support for old on-disk media formats handled by the EFS driver.
