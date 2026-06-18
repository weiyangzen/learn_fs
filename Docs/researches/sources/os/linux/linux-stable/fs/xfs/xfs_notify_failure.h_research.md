# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.h

## Purpose
Tiny header exposing XFS DAX failure notification operations.

## API
Declares `extern const struct dax_holder_operations xfs_dax_holder_operations;`.

## Dependencies
The implementation lives in `xfs_notify_failure.c`; including code must have DAX holder type declarations available through normal kernel headers.
