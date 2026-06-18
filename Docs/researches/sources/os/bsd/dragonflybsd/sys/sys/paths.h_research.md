# File Research: sources/os/bsd/dragonflybsd/sys/sys/paths.h

Kernel/system internal path constant definitions.

Key responsibilities:
- Defines canonical system device paths for console, default tape, null, zero, drum, kmem, mem, tty, and `/dev/`.
- Provides `__SYS_PATH_DEV` with a trailing slash for pathname construction.

Important behavior:
- These are internal `__SYS_PATH_*` names, distinct from userland `_PATH_*` constants.

Dependencies:
- No includes beyond guard.

Notable risks:
- Constants are embedded string ABI assumptions for low-level system components.
- `__SYS_PATH_DEV` intentionally includes a trailing slash, unlike individual device paths.
