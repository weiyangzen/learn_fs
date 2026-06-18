# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.h

## Scope

This header declares OrangeFS debugfs entry points.

## APIs Declared

- `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`.
- `orangefs_prepare_debugfs_help_string()`.
- Device ioctl hooks for client mask, client string, and debug mask updates.

## Dependencies And Role

- Used by module init and `/dev/pvfs2-req` ioctl dispatch.
