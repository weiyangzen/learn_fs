# File Research: sources/os/linux/linux/fs/ecryptfs/kthread.c

## Purpose
Provides a dedicated eCryptfs kernel thread used to open lower files with read/write access when direct open from the caller fails.

## Main Responsibilities
- Start and stop the `ecryptfs-kthread`.
- Maintain a request queue of lower-file open requests.
- Retry lower-file opens from the kernel thread with `O_RDWR | O_LARGEFILE`.
- Complete blocked callers once the lower file is opened or shutdown aborts the request.

## Control Flow
`ecryptfs_privileged_open()` first tries `dentry_open()` with the caller credentials and `O_RDONLY` or `O_RDWR` based on lower inode read-only state. If read/write open fails and read-only was not requested, it queues an `ecryptfs_open_req`, wakes the kthread, waits for completion, and returns the queued result.

`ecryptfs_threadfn()` waits on the control waitqueue, drains queued requests under the control mutex, opens each lower path as `O_RDWR | O_LARGEFILE` using `current_cred()`, stores the result through the request pointer, and completes the request.

`ecryptfs_destroy_kthread()` marks the control state zombie, completes all queued requests with `ERR_PTR(-EIO)`, stops the thread, and wakes the waitqueue.

## State and Locking
- `ecryptfs_kthread_ctl.mux` protects flags and request list.
- `ECRYPTFS_KTHREAD_ZOMBIE` prevents new queued work during teardown.
- Each request uses a stack-allocated completion in the caller.

## Dependencies
- Used by `main.c` lower-file initialization.
- Uses VFS `dentry_open()` and kthread/freezer APIs.

## Risks and Notes
- The function comments describe obtaining lower files with RW permissions, but the direct first attempt may still be read-only for read-only lower inodes.
- During teardown, queued callers receive `-EIO`.
