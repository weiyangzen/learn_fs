# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.c

## Purpose
Implements a small parallel workqueue abstraction for XFS tasks that can split work across multiple process-context workers while tracking completion and first error.

## Main APIs
- `xfs_pwork_init` creates an unbound, sysfs-visible, freezable workqueue and initializes control state.
- `xfs_pwork_queue` initializes and queues an embedded `xfs_pwork`.
- `xfs_pwork_poll` waits for all queued work while touching the soft lockup watchdog.
- `xfs_pwork_destroy` destroys the workqueue and returns the first recorded worker error.

## Key Behavior
Each queued work item invokes the caller’s `work_fn(mp, pwork)`. The first nonzero error is stored in `pctl->error`, but queued work continues to run; worker functions are expected to consult abort helpers if they want early exit. The atomic work count wakes poll waiters when the final item completes.

## Configuration
In debug builds, `xfs_globals.pwork_threads` can override the workqueue concurrency limit. Otherwise the abstraction defaults to an unlimited unbound workqueue concurrency setting.
