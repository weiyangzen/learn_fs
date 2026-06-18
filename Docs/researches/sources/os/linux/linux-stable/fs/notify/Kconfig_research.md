# File Research: sources/os/linux/linux-stable/fs/notify/Kconfig

Purpose: Top-level Kconfig entry point for fsnotify-related kernel configuration.

Core contents:
- Defines `config FSNOTIFY` as `def_bool n`; it is selected by concrete notification features rather than user-selected directly here.
- Sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

Important behavior:
- This file establishes fsnotify as a hidden base symbol for dnotify, inotify, and fanotify.

Dependencies and interfaces:
- Kconfig-only file; no runtime code.

Design notes and risks:
- Any new fsnotify frontend Kconfig should be sourced here to be visible in configuration traversal.
