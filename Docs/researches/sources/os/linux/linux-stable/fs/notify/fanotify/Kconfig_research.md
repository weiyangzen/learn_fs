# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/Kconfig

Purpose: Kconfig options for fanotify support.

Core contents:
- `config FANOTIFY` enables filesystem-wide access notification, selects `FSNOTIFY` and `EXPORTFS`, and defaults to `n`.
- Help text explains that fanotify sends an open file descriptor to user-space listeners along with the event.
- `config FANOTIFY_ACCESS_PERMISSIONS` enables permission checking for fanotify listeners, depends on `FANOTIFY`, and defaults to `n`.

Important behavior:
- Basic fanotify support pulls in fsnotify core and exportfs support.
- Permission checking is separated so access-decision fanotify features can be disabled independently.

Dependencies and interfaces:
- Kconfig-only; informs conditional compilation in fanotify code elsewhere.

Design notes and risks:
- Permission checking has direct security implications and is opt-in, with help text recommending `N` if unsure.
