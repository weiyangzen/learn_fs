# File Research: sources/os/linux/linux-stable/fs/fs_struct.c

## Purpose
Manages `struct fs_struct`, the per-task filesystem context containing root, current working directory, umask, sharing state, and seqlock protection.

## Key Interfaces
- `set_fs_root()` and `set_fs_pwd()` replace root or cwd path references safely.
- `chroot_fs_refs()` rewrites matching root/cwd references across all tasks when a chroot root is moved.
- `free_fs_struct()` drops path references and frees the object.
- `exit_fs()` detaches a task from its fs context and frees it if the last user exits.
- `copy_fs_struct()` clones root, pwd, umask, and seqlock state for unsharing.
- `unshare_fs_struct()` installs a private copy for the current task.
- `init_fs` defines the boot-time initial fs context.

## Design Notes
Path updates use `write_seqlock()` so lockless readers can retry on concurrent mutation. Task-level changes use `task_lock()`, `tasklist_lock`, and exclusive seqlock sections around shared-user counts.

## Dependencies
Relies on VFS path refcounting, task iteration, task locking, `fs_cachep`, seqlocks, and scheduler task structures.

## Research Notes
The main behavioral contract is correct path reference ownership while `fs_struct` may be shared across threads. `chroot_fs_refs()` deliberately counts replaced references and drops old paths after releasing the task list lock.
