# File Research: sources/os/linux/linux/fs/xfs/xfs_pwork.c

## Purpose

`xfs_pwork.c` implements a small parallel workqueue abstraction for XFS tasks that can be split across CPUs. It wraps Linux workqueues with XFS-specific control state, error recording, polling support, and tracing.

## Main Responsibilities

- Initialize a workqueue for a parallel task.
- Queue embedded `struct xfs_pwork` items.
- Invoke a caller-provided work function for each item.
- Record the first nonzero worker error.
- Track outstanding work count.
- Wake pollers when all work completes.
- Destroy the workqueue and return recorded error.
- Provide polling that touches the soft lockup watchdog.

## Important Functions

- `xfs_pwork_init`: allocates an unbound, sysfs-visible, freezable workqueue named from the caller tag and current pid. In debug builds, `xfs_globals.pwork_threads` can cap parallelism.
- `xfs_pwork_queue`: initializes the work item, attaches control state, increments outstanding count, and queues work.
- `xfs_pwork_work`: internal workqueue callback that calls the client function and updates error/completion state.
- `xfs_pwork_destroy`: destroys the workqueue and returns `pctl->error`.
- `xfs_pwork_poll`: waits in one-second intervals for outstanding work to reach zero and touches the softlockup watchdog between waits.

## Concurrency Notes

`pctl->error` records the first observed worker error but does not stop already queued work. Work functions are expected to check `xfs_pwork_want_abort` or `xfs_pwork_ctl_want_abort` if they should stop early after another worker reports failure.
