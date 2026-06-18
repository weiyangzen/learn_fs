# File Research: sources/os/linux/linux-stable/fs/sysctls.c

Purpose: Registers shared `/proc/sys/fs` sysctls used by multiple filesystems.

Key responsibilities:
- Defines `overflowuid` and `overflowgid` sysctl entries.
- Binds them to `fs_overflowuid` and `fs_overflowgid`.
- Uses `proc_dointvec_minmax` with bounds from zero to `SYSCTL_MAXOLDUID`.
- Registers the table under `fs` at early init.

Important interactions:
- Exposes fallback UID/GID behavior through the sysctl subsystem.
- Runs via `early_initcall(init_fs_sysctls)`.

Notable invariants and risks:
- The table is intentionally small and shared rather than filesystem-specific.
