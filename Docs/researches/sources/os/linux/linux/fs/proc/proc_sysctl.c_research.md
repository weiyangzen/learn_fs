# File Research: sources/os/linux/linux/fs/proc/proc_sysctl.c

## Scope

This file implements `/proc/sys`: sysctl table registration, rb-tree directory lookup, proc inode/dentry operations, read/write handler dispatch, polling, namespace/set links, unregister invalidation, and command-line `sysctl.` argument application.

## Public And Internal APIs Covered

- Registration: `register_sysctl_mount_point()`, `__register_sysctl_table()`, `register_sysctl_sz()`, `__register_sysctl_init()`, `unregister_sysctl_table()`.
- Poll notification: `proc_sys_poll_notify()`.
- Sysctl set lifecycle: `setup_sysctl_set()`, `retire_sysctl_set()`.
- Proc init: `proc_sys_init()`.
- Command-line handling: `sysctl_is_alias()`, `do_sysctl_args()`.
- Proc operations: `proc_sys_file_operations`, `proc_sys_dir_file_operations`, `proc_sys_inode_operations`, `proc_sys_dir_operations`, `proc_sys_dentry_operations`.

## Control Flow And Behavior

- Sysctl entries are represented by `ctl_table_header` objects containing `ctl_node` rb-tree nodes. A global `sysctl_lock` protects tree mutation, use counts, unregister state, and inode sibling lists.
- `insert_header()` attaches a header under a `ctl_dir`, rejects writes under permanently empty mount-point directories, creates namespace links when needed, inserts every entry into the parent rb-tree, and rolls back on failure.
- Lookup starts from a directory header, finds an rb-tree entry by proc name, follows namespace symlinks when needed, then creates a proc inode with `proc_sys_make_inode()`.
- `proc_sys_make_inode()` links the new proc inode to the sysctl header sibling list, increments header count, sets file or directory operations based on table mode, applies root ownership callbacks, and creates empty directory inodes for permanently empty headers.
- Reads and writes route through `proc_sys_call_handler()`: it pins the header, checks sysctl permissions, allocates a kernel buffer, copies write input, runs BPF cgroup sysctl hooks, calls the table's `proc_handler`, and copies read output.
- Polling stores the current poll event in `file->private_data` and reports changes after `proc_sys_poll_notify()`.
- Directory readdir walks usable rb-tree entries, follows symlink entries when needed, fills/creates dcache children, and emits dirents.
- Permission checks intentionally do not grant root automatic writes to read-only sysctls. Regular files under `/proc/sys` deny execute.
- Dentry operations force revalidation outside RCU, delete unregistering entries, and compare namespace visibility so dentries from unseen sets are not reused.
- Directory creation uses `sysctl_mkdir_p()` and `get_subdir()` to create missing intermediate `ctl_dir` objects with reference transfer down the path.
- Namespace-specific sets can create symlink placeholder entries in the root sysctl set. `sysctl_follow_link()` translates a link into the corresponding visible table in the active set.
- Unregistering uses `drop_sysctl_table()` and `start_unregistering()` to wait for active users, invalidate dentries for associated inodes, remove rb-tree nodes, release links, and free headers with RCU after all references drain.
- `do_sysctl_args()` parses the saved command line, recognizes `sysctl.<path>=value` and historical aliases, mounts a temporary procfs instance lazily, opens `sys/<path>`, writes the value, logs failures, and unmounts.

## Dependencies

- Depends on sysctl core structures, proc inode helpers, dcache invalidation from `inode.c`, BPF cgroup sysctl hooks, VFS path/open/write APIs, fs parser command-line argument parsing, RCU freeing, completions, and security/credential APIs.

## Risks And Invariants

- `used`, `count`, `nreg`, and `unregistering` have distinct meanings; unregister waits for active handler calls before removing entries and frees only after inode/header references drain.
- Table validation requires proc names, handlers, data/maxlen for standard handlers, valid modes, and non-array uses for scalar handlers.
- Permanently empty mount point headers prevent later children and preserve permission behavior for unprivileged mounts.
- Namespace link insertion/removal must stay balanced or root-set symlink entries can become stale.
- `proc_sys_call_handler()` copies sysctl data through a temporary kernel buffer and enforces `KMALLOC_MAX_SIZE` to avoid oversized allocations.
