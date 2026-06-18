# File Research: sources/os/linux/linux-stable/fs/ecryptfs/kthread.c

## Summary
Provides the eCryptfs kernel thread used as a fallback path for opening lower files with read/write access when direct open under caller credentials fails.

## Main Responsibilities
- Maintain a request queue of lower-file open requests.
- Run `ecryptfs-kthread`, which processes queued `dentry_open()` requests.
- Initialize and destroy thread control state at module load/unload.
- Mark shutdown with `ECRYPTFS_KTHREAD_ZOMBIE` and complete pending requests with `-EIO`.
- Implement `ecryptfs_privileged_open()` for lower-file acquisition.

## Key APIs
- `ecryptfs_init_kthread()`
- `ecryptfs_destroy_kthread()`
- `ecryptfs_privileged_open()`

## Important Behavior
`ecryptfs_privileged_open()` first tries to open the lower file directly with `O_RDONLY` for read-only lower inodes or `O_RDWR` otherwise. If an `O_RDWR` direct open fails, it queues a request to the eCryptfs kernel thread, waits for completion, and returns the resulting lower file or error.

The kthread is freezable and exits when the zombie flag is set. Pending requests are completed during teardown so callers do not sleep indefinitely.

## Research Notes
This file supports the one-lower-file-per-inode model in `main.c`. Its key invariant is completion of every queued request, including during shutdown.
