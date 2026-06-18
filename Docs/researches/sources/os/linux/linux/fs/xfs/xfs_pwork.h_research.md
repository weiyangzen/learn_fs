# File Research: sources/os/linux/linux/fs/xfs/xfs_pwork.h

## Purpose

`xfs_pwork.h` declares the XFS parallel work abstraction.

## Main Types

- `xfs_pwork_work_fn`: callback signature taking mount and pwork item.
- `struct xfs_pwork_ctl`: owns workqueue, mount pointer, callback, waitqueue, outstanding work count, and first error.
- `struct xfs_pwork`: embeddable work item with Linux `work_struct` and backpointer to the control object.

## Public API

- `xfs_pwork_init`
- `xfs_pwork_queue`
- `xfs_pwork_destroy`
- `xfs_pwork_poll`

## Helpers

- `XFS_PWORK_SINGLE_THREADED`: initializer for non-queued single-threaded usage.
- `xfs_pwork_ctl_want_abort`: true if control object exists and has an error.
- `xfs_pwork_want_abort`: checks abort state from an embedded pwork item.

## Notes

The abstraction is intentionally thin. It does not cancel queued work on first error; it exposes the error state so workers and callers can decide how aggressively to stop.
