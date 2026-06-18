# File Research: sources/os/linux/linux-stable/fs/ntfs/sysctl.c

This file provides optional sysctl support for the legacy `fs/ntfs` driver debug flag.

Main responsibilities:
- Compiles only when `DEBUG` is defined; the actual sysctl registration compiles only with `CONFIG_SYSCTL`.
- Defines a single sysctl table entry, `fs/ntfs/ntfs-debug`, backed by the global `debug_msgs` integer from `debug.h`.
- Provides `ntfs_sysctl(int add)` to register or unregister the table during module init/exit.

Important functions and data:
- `ntfs_sysctls[]` contains the `procname`, data pointer, size, permissions `0644`, and `proc_dointvec` handler.
- `sysctls_root_table` stores the registration handle returned by `register_sysctl()`.
- `ntfs_sysctl(1)` registers under `fs/ntfs`; `ntfs_sysctl(0)` unregisters and clears the handle.

Research notes:
- In non-debug builds this file contributes no code; callers rely on the inline no-op in `sysctl.h`.
- The sysctl is strictly a debug-message control and has no mount or metadata behavior.
