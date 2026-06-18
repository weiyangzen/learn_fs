# File Research: sources/os/linux/linux/fs/notify/inotify/Makefile

## Role

This Makefile builds the inotify userspace implementation when `CONFIG_INOTIFY_USER` is enabled.

## Objects

It links two objects into the fsnotify/inotify portion of the kernel:

- `inotify_fsnotify.o`
- `inotify_user.o`

## Design Notes

The split mirrors the subsystem boundary: fsnotify backend event handling is separate from syscall and fd operations.
