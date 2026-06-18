# File Research: sources/os/linux/linux/fs/proc/self.c

## Scope

This file implements the persistent `/proc/self` symlink.

## Public And Internal APIs Covered

- Symlink target callback: `proc_self_get_link()`.
- Setup: `proc_setup_self()`.
- Inode-number allocation: `proc_self_init()`.
- Global inode number: `self_inum`.

## Control Flow And Behavior

- `proc_self_get_link()` resolves the current task's thread group ID in the proc superblock's PID namespace and returns it as a freshly allocated decimal string.
- If the current task has no TGID in that namespace, it returns `-ENOENT`.
- `proc_setup_self()` allocates a persistent dentry and symlink inode under the proc root using `self_inum`.
- `proc_self_init()` allocates the stable proc inode number during root initialization.

## Dependencies And Risks

- Depends on PID namespace translation through `proc_pid_ns()` and `task_tgid_nr_ns()`.
- Allocation mode uses `GFP_ATOMIC` during RCU-style delayed link resolution when no dentry is supplied.
