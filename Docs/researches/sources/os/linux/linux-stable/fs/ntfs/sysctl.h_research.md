# File Research: sources/os/linux/linux-stable/fs/ntfs/sysctl.h

This header declares or stubs the legacy NTFS debug sysctl registration function.

Main responsibilities:
- Provides the include guard `_LINUX_NTFS_SYSCTL_H`.
- Declares `int ntfs_sysctl(int add);` only for `DEBUG && CONFIG_SYSCTL`.
- Provides an inline no-op `ntfs_sysctl()` returning success for all other builds.

Research notes:
- This lets `super.c` call `ntfs_sysctl(1)` and `ntfs_sysctl(0)` unconditionally in module init/exit.
- The stub preserves identical control flow in production configurations without requiring extra preprocessor branches in the caller.
