# File Research: sources/os/linux/linux/fs/notify/dnotify/Kconfig

Purpose: Kconfig option for legacy dnotify support.

Core contents:
- Defines user-visible boolean `DNOTIFY`.
- Selects `FSNOTIFY`.
- Defaults to `y`.
- Help describes dnotify as directory-based per-fd notification using signals, retained for compatibility despite superior alternatives.

Important behavior:
- Enabling dnotify automatically enables fsnotify core.

Dependencies and interfaces:
- Kconfig-only file.

Design notes and risks:
- Defaulting to `y` preserves compatibility for applications still relying on dnotify.
