# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/Kconfig

Purpose: Kconfig option for legacy dnotify support.

Core contents:
- Defines `config DNOTIFY` as a boolean user-visible option `"Dnotify support"`.
- Selects `FSNOTIFY`.
- Defaults to `y`.
- Help text describes dnotify as a directory-based per-file-descriptor file change notification system using signals, retained for compatibility despite better alternatives.

Important behavior:
- Enabling dnotify automatically enables fsnotify core.

Dependencies and interfaces:
- Kconfig-only.

Design notes and risks:
- Defaulting to `y` preserves compatibility for applications that still rely on dnotify.
