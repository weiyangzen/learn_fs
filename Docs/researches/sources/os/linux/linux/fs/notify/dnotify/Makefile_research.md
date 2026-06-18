# File Research: sources/os/linux/linux/fs/notify/dnotify/Makefile

Purpose: Kbuild rule for the dnotify implementation.

Core contents:
- Builds `dnotify.o` when `CONFIG_DNOTIFY` is enabled.

Important behavior:
- This subdirectory contributes code only under the dnotify config symbol.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Implementation is a single C object.
