# File Research: sources/os/linux/linux/fs/ntfs/sysctl.c

Read coverage: complete file, 54 lines.

This file implements optional debug sysctl registration for the NTFS driver, compiled only when both `DEBUG` and `CONFIG_SYSCTL` are enabled.

Key logic:
- Defines a single sysctl table entry under `fs/ntfs` named `ntfs-debug`.
- The sysctl exposes the global `debug_msgs` integer through `proc_dointvec` with mode `0644`.
- `ntfs_sysctl(int add)` registers the table when `add` is true and unregisters it when false.
- Registration failure returns `-ENOMEM`; removal clears the saved `ctl_table_header *`.

Integration:
- Called from `super.c` module init/exit.
- Includes `debug.h`, where `debug_msgs` is declared/used by the NTFS debug infrastructure.

Risk:
- Only active in debug builds with sysctl support. Normal builds use the inline no-op from `sysctl.h`.
