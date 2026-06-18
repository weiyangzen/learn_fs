# File Research: sources/os/linux/linux-stable/fs/proc/root.c

Implements procfs filesystem registration, mount context parsing, root superblock setup, and root directory behavior.

Key points:
- Defines mount context options: `gid`, `hidepid`, `subset`, and `pidns`.
- `hidepid` accepts numeric or string values: `off`, `noaccess`, `invisible`, `ptraceable`.
- `subset=pid` restricts visible proc content to PID-related subset.
- `pidns=` can accept an nsfs file/path on new mounts, checks `CAP_SYS_ADMIN` in target user namespace and descendant relationship, and cannot be reconfigured.
- `proc_fill_super()` allocates `proc_fs_info`, sets proc superblock flags/magic/ops, creates root inode from `proc_root`, and installs persistent `self` and `thread-self`.
- `proc_reconfigure()` reapplies mutable mount options.
- `proc_kill_sb()` drops pid namespace and frees fs info after anonymous superblock teardown.
- `proc_root_init()` initializes proc caches, special symlinks/directories, net, tty, sysctl, and registers filesystem last.
- Root readdir combines static proc entries first, then PID directories at `FIRST_PROCESS_ENTRY`.
- `proc_root` is the static root PDE.

Dependencies/contracts:
- Mount-time policy root for PID namespace and hidepid behavior.
- Uses `proc_sops` from `inode.c` and generic/PID proc directory handlers.
