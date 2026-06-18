# File Research: sources/os/linux/linux-stable/fs/lockd/procfs.h

Header for lockd procfs support.

Behavior:
- When `CONFIG_PROC_FS` is enabled, declares `lockd_create_procfs()` and `lockd_remove_procfs()`.
- Otherwise provides inline no-op implementations, with create returning success.
