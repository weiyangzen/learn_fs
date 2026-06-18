# File Research: sources/os/linux/linux-stable/fs/btrfs/async-thread.h

## Summary
Declares Btrfs asynchronous workqueue types and APIs.

## Main Contents
- Function pointer types for normal and ordered work.
- `struct btrfs_work`, embedding kernel work item, ordered-list node, owning Btrfs workqueue, and flags.
- Workqueue allocation, ordered allocation, initialization, queue, destroy, max-active update, owner lookup, congestion query, and flush declarations.

## Risks
`struct btrfs_work` documents that fields below callbacks are internal. Callers must not touch work internals after queueing or after callbacks that may free the work item.
