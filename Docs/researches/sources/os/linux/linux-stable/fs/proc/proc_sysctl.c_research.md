# File Research: sources/os/linux/linux-stable/fs/proc/proc_sysctl.c

Implements `/proc/sys` sysctl registration, lookup, inode materialization, reads/writes, polling, unregister, namespace links, and boot-time sysctl argument handling.

Key points:
- Maintains sysctl directories as rb-trees of `ctl_node` entries protected by `sysctl_lock`.
- `ctl_table_header` has `used`, `count`, `nreg`, unregister completion, parent, root, set, and sibling inode list state.
- `insert_header()` inserts tables and creates namespace link entries when needed.
- `start_unregistering()` waits for active users, invalidates proc dentries, then erases entries.
- `proc_sys_make_inode()` creates proc inodes for sysctl entries and links them into header inode lists for invalidation/eviction.
- File IO routes through `proc_sys_call_handler()`:
  - checks permission
  - allocates kernel buffer
  - copies write input
  - runs BPF cgroup sysctl hook
  - calls table `proc_handler`
  - copies read output
- Poll support uses `ctl_table_poll`.
- Directory lookup/readdir follows sysctl links and fills dcache entries.
- Dentry ops revalidate/delete on unregister and compare visibility for namespaced sysctls.
- Registration validates table shape, handlers, mode bits, data pointers, maxlen, and scalar handler array restrictions.
- `register_sysctl_mount_point()` supports permanently empty sysctl directories for mount points.
- `do_sysctl_args()` parses kernel command-line sysctl aliases/options by temporarily mounting procfs and writing `/proc/sys/...`.

Dependencies/contracts:
- Central sysctl proc ABI.
- Interacts with BPF cgroup sysctl hooks, security/permission model, proc inode eviction, dcache invalidation, and namespace-specific sysctl sets.
