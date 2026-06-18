# File Research: sources/os/linux/linux-stable/fs/notify/Makefile

Purpose: Build rules for the fsnotify subsystem directory.

Core contents:
- Builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o` when `CONFIG_FSNOTIFY` is enabled.
- Always descends into `dnotify/`, `inotify/`, and `fanotify/` via `obj-y`, letting subdirectory Makefiles decide based on config symbols.

Important behavior:
- Core fsnotify objects are conditional on `CONFIG_FSNOTIFY`.
- Frontend directories are included in the build traversal unconditionally.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- The multiline `obj-$(CONFIG_FSNOTIFY)` assignment is the central list for shared fsnotify infrastructure objects.
