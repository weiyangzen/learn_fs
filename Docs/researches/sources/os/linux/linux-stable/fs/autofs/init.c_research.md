# File Research: sources/os/linux/linux-stable/fs/autofs/init.c

## Purpose
Defines module initialization/exit and the autofs filesystem type.

## Main Interfaces
- `autofs_fs_type`.
- `init_autofs_fs()`.
- `exit_autofs_fs()`.

## Important Behavior
Module init registers the `/dev/autofs` miscdevice first, then registers the `autofs` filesystem. If filesystem registration fails, it deregisters the miscdevice. Module exit reverses that by deregistering the miscdevice and unregistering the filesystem.

## Cross-File Relationships
Connects `autofs_init_fs_context()` from `inode.c`, `autofs_kill_sb()` from `inode.c`, mount parameters from `autofs_i.h`, and miscdevice setup from `dev-ioctl.c`.

## Risks / Review Notes
Initialization ordering matters because the device interface and filesystem registration are exposed independently. Failure handling currently cleans up the miscdevice if filesystem registration fails.
