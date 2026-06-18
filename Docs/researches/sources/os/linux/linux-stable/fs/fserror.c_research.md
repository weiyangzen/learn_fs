# File Research: sources/os/linux/linux-stable/fs/fserror.c

## Purpose
Implements generic filesystem error event reporting. Filesystems can report errors to superblock callbacks and fsnotify while keeping event delivery safe from atomic contexts.

## Key Interfaces
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias reference.
- `fserror_unmount()` drops the bias and waits for queued error events to drain.
- `fserror_report()` allocates an event, validates inputs, optionally grabs an inode reference, and schedules worker delivery.
- `fserror_worker()` invokes `sb->s_op->report_error()` if present and sends an `FS_ERROR` fsnotify event.
- `fserror_init()` initializes a mempool for error events.

## Design Notes
Pending events are tracked with a superblock refcount so unmount can wait for asynchronous workers. Events are allocated from a mempool to improve reliability in error paths. Workqueue delivery avoids calling filesystem callbacks or fsnotify from atomic contexts or while locks are held.

## Dependencies
Uses `fsnotify`, superblock operations, inode refcounting, workqueues, mempools, and `linux/fserror.h`.

## Research Notes
Lost reports are ratelimited to the kernel log. The code assumes reported `error` values are negative and warns if inode and superblock do not belong together.
