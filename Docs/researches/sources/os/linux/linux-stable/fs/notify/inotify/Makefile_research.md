# File Research: sources/os/linux/linux-stable/fs/notify/inotify/Makefile

## Summary
Build rule for inotify userspace support.

## Contents
When `CONFIG_INOTIFY_USER` is enabled, builds `inotify_fsnotify.o` and `inotify_user.o`.

## Risks
The split matches backend event handling in `inotify_fsnotify.c` and syscall/fd/mark management in `inotify_user.c`; both are required for a working userspace inotify implementation.
