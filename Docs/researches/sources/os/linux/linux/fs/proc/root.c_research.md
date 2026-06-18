# File Research: sources/os/linux/linux/fs/proc/root.c

## Scope

This file implements procfs mount context parsing, superblock creation, reconfiguration, teardown, root directory operations, and global proc root initialization.

## Public And Internal APIs Covered

- Mount context: `struct proc_fs_context`, `proc_fs_parameters`, `proc_fs_context_ops`.
- Filesystem type: `proc_fs_type`.
- Init: `proc_root_init()`.
- Root PDE: `proc_root`.
- Root inode and file ops: `proc_root_inode_operations`, `proc_root_operations`.

## Control Flow And Behavior

- Supported mount parameters are `gid=`, `hidepid=`, `subset=`, and `pidns=`.
- `proc_parse_hidepid_param()` accepts numeric values and strings: `off`, `noaccess`, `invisible`, and `ptraceable`.
- `proc_parse_subset_param()` currently supports only `subset=pid`.
- `proc_parse_pidns_param()` accepts a file or path to an nsfs PID namespace file, verifies namespace type, checks `CAP_SYS_ADMIN` in the target user namespace, requires the target pidns to be a descendant of the caller's active pidns, and updates the fs context user namespace.
- `proc_apply_options()` applies parsed options to `proc_fs_info`, disallowing `subset=pid` changes on reconfigure and disallowing pidns changes on existing procfs instances.
- `proc_fill_super()` allocates `proc_fs_info`, stores pid namespace and mounter credentials, applies options, sets procfs superblock flags, creates the root inode from `proc_root`, creates the root dentry, and installs persistent `self` and `thread-self` symlinks.
- `proc_init_fs_context()` seeds new mounts with the caller's active PID namespace and switches the fs context user namespace to that pidns user namespace.
- `proc_kill_sb()` tears down the anonymous superblock, releases pid namespace and mounter credentials, and RCU-frees `proc_fs_info`.
- `proc_root_init()` initializes caches, PID link counts, self symlink inode numbers, top-level symlinks and directories, proc net/sys/tty subtrees, then registers the proc filesystem.
- Root lookup checks numeric PID directories before generic proc entries. Root readdir emits static proc entries first, then PID directories from offset `FIRST_PROCESS_ENTRY`.
- `proc_root_getattr()` reports link count as static proc root links plus current process count.

## Dependencies

- Depends on fs_context/fs_parser, PID namespaces, user namespaces, proc inode creation, proc generic directory operations, proc PID lookup/readdir, self/thread-self setup, proc net/sys/tty initialization, and superblock helpers.

## Risks And Invariants

- Procfs mounts are user-namespace mountable but restricted and force noexec/nodev/nosuid semantics.
- `pidns=` cannot be reconfigured because too many procfs accesses assume stable `proc_fs_info`.
- `subset=pid` cannot be changed on reconfigure because it changes the static visible tree variant.
- Root directory offsets reserve low positions for static entries and start process entries at `FIRST_PROCESS_ENTRY`.
