# File Research: sources/os/linux/linux/fs/xfs/xfs_notify_failure.h

## Purpose

`xfs_notify_failure.h` declares the XFS DAX holder operations object used for media failure notification.

## Public Interface

- `extern const struct dax_holder_operations xfs_dax_holder_operations;`

## Notes

The implementation is in `xfs_notify_failure.c`. This header intentionally contains only the external declaration and include guard.
