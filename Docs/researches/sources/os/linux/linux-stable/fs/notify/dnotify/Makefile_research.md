# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/Makefile

Purpose: Build rule for dnotify implementation.

Core contents:
- Builds `dnotify.o` when `CONFIG_DNOTIFY` is enabled.

Important behavior:
- This subdirectory contributes code only if the dnotify Kconfig symbol is enabled.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- No composite object list exists here; the implementation is a single C file.
