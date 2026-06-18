# File Research: sources/os/linux/linux/fs/proc/thread_self.c

## Scope

This file implements the persistent `/proc/thread-self` symlink.

## Public And Internal APIs Covered

- Symlink target callback: `proc_thread_self_get_link()`.
- Setup: `proc_setup_thread_self()`.
- Inode-number allocation: `proc_thread_self_init()`.
- Global inode number: `thread_self_inum`.

## Control Flow And Behavior

- `proc_thread_self_get_link()` resolves current TGID and TID in the proc superblock's PID namespace and formats `<tgid>/task/<tid>`.
- If the current thread has no PID in the namespace, it returns `-ENOENT`.
- `proc_setup_thread_self()` creates a persistent symlink inode under the proc root using `thread_self_inum`.
- `proc_thread_self_init()` allocates the stable proc inode number at root initialization time.

## Dependencies And Risks

- Depends on PID namespace translation through `task_tgid_nr_ns()` and `task_pid_nr_ns()`.
- The allocated target buffer is sized for decimal TGID, `/task/`, decimal TID, and NUL.
