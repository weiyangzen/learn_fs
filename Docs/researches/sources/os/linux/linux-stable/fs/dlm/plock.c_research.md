# File Research: sources/os/linux/linux-stable/fs/dlm/plock.c

## Purpose
`plock.c` implements DLM-assisted POSIX file locking. It forwards lock/unlock/get/cancel operations to userspace `dlm_controld` through a misc device and mirrors successful locks into the local VFS lock state.

## Core State
- `send_list`: operations waiting for userspace to read.
- `recv_list`: operations sent to userspace and waiting for a reply.
- `ops_lock`: protects both lists.
- `send_wq` and `recv_wq`: wake readers and waiting kernel callers.
- `struct plock_op`: one operation plus `dlm_plock_info` and optional async data.
- `struct plock_async_data`: saved `file_lock`, callback, and file pointer for async lock handling.

## Kernel API
Exports:
- `dlm_posix_lock()`
- `dlm_posix_unlock()`
- `dlm_posix_cancel()`
- `dlm_posix_get()`

`dlm_posix_lock()` sends a lock request. Blocking calls wait on `recv_wq`; interruptible waits try to send a cancel request. Async locks with `fl_lmops->lm_grant` return `FILE_LOCK_DEFERRED`.

`dlm_posix_unlock()` first unlocks locally through VFS, then sends an unlock to userspace unless it is a close-generated unlock that does not need a reply.

`dlm_posix_cancel()` currently only supports async requests and relies on userspace cancel synchronization.

`dlm_posix_get()` asks userspace for conflicting lock information and converts positive conflict results into a `struct file_lock`.

## Misc Device
`dlm_plock_init()` registers the `DLM_PLOCK_MISC_NAME` misc device. Its operations are:
- `dev_read()`: userspace reads one pending operation from `send_list`.
- `dev_write()`: userspace writes one result matching an operation on `recv_list`.
- `dev_poll()`: signals when operations are available.

Waiting lock replies can arrive out of order and are matched by all lock identity fields. Non-waiting replies are matched to the first non-waiting op for the same filesystem id.

## Risks and Notes
The async callback path logs a “dangling lock” warning if a granted lock notification fails after local state is updated. Comments explicitly note cancellation limitations for non-async waiting requests.
