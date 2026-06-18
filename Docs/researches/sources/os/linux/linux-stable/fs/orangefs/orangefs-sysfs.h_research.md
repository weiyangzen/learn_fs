# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.h

## Scope

This header declares the OrangeFS sysfs lifecycle interface.

## APIs Declared

- `orangefs_sysfs_init()`.
- `orangefs_sysfs_exit()`.

## Dependencies And Role

- Included by module lifecycle code to create and remove `/sys/fs/orangefs` entries.
