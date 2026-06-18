# File Research: sources/os/linux/linux/fs/notify/Makefile

Purpose: Kbuild rules for the fsnotify subsystem directory.

Core contents:
- Builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o` when `CONFIG_FSNOTIFY` is enabled.
- Always descends into `dnotify/`, `inotify/`, and `fanotify/` using `obj-y`.

Important behavior:
- Shared fsnotify infrastructure is conditional on `CONFIG_FSNOTIFY`.
- Frontend subdirectories are traversed unconditionally; their own Makefiles gate objects by config.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- The multiline `obj-$(CONFIG_FSNOTIFY)` list is the central shared fsnotify object list.
