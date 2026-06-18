# File Research: sources/os/linux/linux-stable/fs/proc/fd.c

## Purpose

Implements `/proc/<pid>/fd`, `/proc/<pid>/fdinfo`, and their per-file descriptor entries.

## Main Responsibilities

- `/fdinfo/<fd>` file output:
  - `seq_show()` resolves the target task and fd, prints file position, flags, mount id, inode number, file locks, and optional `show_fdinfo()`.
  - `seq_fdinfo_open()` uses `single_open()`.
- Permission model:
  - `proc_fdinfo_permission()` requires ptrace read access in addition to generic permission.
  - `proc_fd_permission()` allows normal permission or same-thread-group access, supporting `/proc/self/fd` after setuid exec.
- FD symlink behavior:
  - `tid_fd_mode()` reads target fd mode.
  - `tid_fd_update_inode()` updates dynamic owner/mode/security state.
  - `tid_fd_revalidate()` validates fd entries and refreshes inode metadata.
  - `proc_fd_link()` returns the path for a task fd.
  - `proc_fd_instantiate()` creates symlink inodes for `/fd/<fd>`.
- Directory lookup and iteration:
  - `proc_lookupfd_common()` parses numeric fd names and instantiates fd/fdinfo entries.
  - `proc_readfd_common()` iterates open fds via `fget_task_next()` and emits cache entries.
  - `proc_readfd_count()` counts open fds for directory size.
- Exports operations:
  - `proc_fd_operations`, `proc_fd_inode_operations`.
  - `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`.

## Key Data/Control Flow

- `proc_fd()` from `fd.h` stores the fd number in `PROC_I(inode)->fd`.
- fd directory entries are dentry-revalidated because target fds can close or change.
- `/fd/<fd>` symlink permissions reflect read/write mode: read fds get read/execute bits; write fds get write/execute bits.

## Concurrency Notes

- Uses task locking and `files->file_lock` for direct lookup in `seq_show()`.
- Uses `fget_task()`/`fget_task_next()` helpers to safely hold file references while inspecting fd state.
