# File Research: sources/os/linux/linux/fs/notify/Kconfig

Purpose: Top-level Kconfig entry point for fsnotify-related configuration.

Core contents:
- Defines hidden `config FSNOTIFY` with `def_bool n`.
- Sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

Important behavior:
- `FSNOTIFY` is selected by concrete notification frontends rather than directly enabled here.

Dependencies and interfaces:
- Kconfig-only file; no runtime code.

Design notes and risks:
- New fsnotify frontend Kconfig files need to be sourced here to participate in configuration traversal.
