# File Research: sources/os/linux/linux/fs/notify/fanotify/Kconfig

Purpose: Kconfig options for fanotify support.

Core contents:
- `config FANOTIFY` enables filesystem-wide access notification, selects `FSNOTIFY` and `EXPORTFS`, and defaults to `n`.
- Help notes fanotify sends an open file descriptor to userspace listeners with events.
- `config FANOTIFY_ACCESS_PERMISSIONS` depends on `FANOTIFY`, enables listener permission decisions, and defaults to `n`.

Important behavior:
- Basic fanotify support pulls in fsnotify core and exportfs support.
- Permission checking is independently configurable.

Dependencies and interfaces:
- Kconfig-only file; controls fanotify compilation and feature availability elsewhere.

Design notes and risks:
- Permission checking is security-sensitive and defaults off, with help text recommending `N` if unsure.
