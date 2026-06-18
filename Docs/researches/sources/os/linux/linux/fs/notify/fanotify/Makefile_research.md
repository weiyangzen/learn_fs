# File Research: sources/os/linux/linux/fs/notify/fanotify/Makefile

Purpose: Kbuild rule for fanotify implementation files.

Core contents:
- Builds `fanotify.o` and `fanotify_user.o` when `CONFIG_FANOTIFY` is enabled.

Important behavior:
- Core event handling/allocation is in `fanotify.o`.
- User-facing syscall/read/response logic is in `fanotify_user.o`, outside this work item.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Source layout changes must keep this object list synchronized.
