# File Research: sources/os/linux/linux/fs/fserror.c

## Purpose
This file implements asynchronous filesystem error reporting from superblocks to filesystem-specific callbacks and to fsnotify/userspace. It allows errors discovered in contexts that may not sleep to be queued to process context while preserving inode references until reporting completes.

## Main Definitions
- `FSERROR_DEFAULT_EVENT_POOL_SIZE` sets the mempool baseline to 32 events.
- Global `fserror_events_pool` backs allocations for `struct fserror_event`.
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias of one.
- `fserror_unmount()` drops the bias and waits for pending queued events to drain.
- `fserror_worker()` invokes optional `sb->s_op->report_error(event)` and emits an `FS_ERROR` fsnotify event.
- `fserror_report()` is the public reporting API and is exported GPL.
- `fserror_init()` initializes the mempool at `fs_initcall` time.

## Control Flow And Behavior
`fserror_report()` validates that `inode->i_sb` matches `sb` and that `error` is negative, allocates an event while incrementing `s_pending_errors`, fills event details, grabs an inode reference with `igrab()` when present, and schedules work. The worker converts the stored negative errno to a positive userspace error code for `fs_error_report`, calls filesystem-specific reporting if provided, sends an fsnotify event, drops the inode, and decrements the pending counter.

If allocation or inode grabbing fails, the code drops any pending reference and logs a rate-limited lost-report message.

## Dependencies And Interfaces
This file uses superblock fields, inode references, workqueues, mempools, fsnotify, and the `struct fserror_event` / `struct fs_error_report` API from `<linux/fserror.h>`.

## Concurrency And Safety
`s_pending_errors` is a refcount used as an unmount barrier. `refcount_inc_not_zero()` prevents queuing new reports after shutdown begins. The worker only reports while `SB_ACTIVE` is still set. Barriers are provided by refcount operations, as noted in the source comments.

## Research Notes
The design assumes filesystem errors are rare and favors process-context safety over immediate delivery. The unmount path blocks until queued reports drain, which prevents event memory and inode references from outliving the superblock teardown.
