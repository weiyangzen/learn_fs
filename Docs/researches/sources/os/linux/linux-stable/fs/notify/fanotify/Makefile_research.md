# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/Makefile

Purpose: Build rule for fanotify implementation files.

Core contents:
- Builds `fanotify.o` and `fanotify_user.o` when `CONFIG_FANOTIFY` is enabled.

Important behavior:
- Fanotify is split between core event handling/allocation (`fanotify.o`) and user-facing syscall/read-response handling (`fanotify_user.o`, not in this work item).

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Any changes to fanotify source layout must keep this composite list synchronized.
