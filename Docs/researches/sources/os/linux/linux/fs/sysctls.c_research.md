# File Research: sources/os/linux/linux/fs/sysctls.c

Purpose: Registers shared `/proc/sys/fs` sysctls used by multiple filesystems.

Key behavior:
- Defines `fs_shared_sysctls` with `overflowuid` and `overflowgid`.
- Both sysctls use `proc_dointvec_minmax`, mode `0644`, lower bound `SYSCTL_ZERO`, and upper bound `SYSCTL_MAXOLDUID`.
- `init_fs_sysctls()` registers the table under `"fs"` using `register_sysctl_init`.
- Registration runs via `early_initcall`.

Dependencies:
- Global `fs_overflowuid` and `fs_overflowgid` variables from filesystem core headers.
