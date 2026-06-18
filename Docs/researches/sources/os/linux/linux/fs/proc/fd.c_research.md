# File Research: sources/os/linux/linux/fs/proc/fd.c

## Purpose
Implements `/proc/<pid>/fd` symlink directories and `/proc/<pid>/fdinfo` metadata directories for task file descriptors.

## Main Responsibilities
- Lists open file descriptors for a task.
- Instantiates fd symlinks that resolve to the file path of a specific descriptor.
- Instantiates fdinfo regular files that show position, flags, mount ID, inode number, locks, and file-specific fdinfo.
- Enforces ptrace-read permissions for fdinfo.
- Provides same-thread-group permission bypass for `/proc/self/fd` use after setuid-like transitions.
- Updates fd symlink inode mode based on target file read/write mode.

## Key Interfaces
- `proc_fd_operations`
- `proc_fd_inode_operations`
- `proc_fdinfo_operations`
- `proc_fdinfo_inode_operations`
- `proc_fd_permission()`
- Internal helpers: `proc_fd_link()`, `proc_fd_instantiate()`, `proc_fdinfo_instantiate()`, `proc_readfd_common()`, `proc_lookupfd_common()`.

## Control Flow and Data Handling
Fd lookup parses the dentry name as an integer fd, gets the task, verifies the fd exists via `fget_task()`, records the file mode, and instantiates either a symlink or fdinfo file.

Directory iteration emits dots, then repeatedly calls `fget_task_next()` to find the next open fd from the task’s file table. Each fd is passed to `proc_fill_cache()` to create dcache-consistent entries.

Fdinfo reads acquire the task and file under task/file locks, snapshot flags including close-on-exec, take a file reference, release task locks, then print metadata and optional file-specific information.

## Dependencies and Integration
Uses procfs inode helpers from `base.c`, file descriptor tables, path/mount internals, file locks, ptrace checks, LSM inode labeling, and VFS link operations.

## Concurrency and Lifetime Notes
The code takes task references and file references before using task file data outside locks. Dentry revalidation checks that the fd still exists and refreshes inode ownership/mode. `pid_delete_dentry()` removes stale entries when the task exits.

## Risks and Review Hotspots
- fd table iteration races with close/open; file references must be taken before use.
- fdinfo exposes sensitive state and therefore requires ptrace read permission.
- `/proc/<pid>/fd` permission behavior is intentionally special for same-thread-group access.
- Symlink mode is derived from file mode and can change as the fd target changes.
