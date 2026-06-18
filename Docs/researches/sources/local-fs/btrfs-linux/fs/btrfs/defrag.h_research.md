# File Research: sources/local-fs/btrfs-linux/fs/btrfs/defrag.h

## Purpose

Declares the Btrfs defragmentation interface used by ioctl paths, autodefrag scheduling, filesystem lifecycle code, and tree defrag callers.

## Main Responsibilities

- Exposes file defrag, root defrag, autodefrag init/exit, inode queueing, queue draining, and cleanup APIs.
- Provides the cancellation helper used by defrag loops.

## Public API

- `btrfs_defrag_file()` defragments a file range using ioctl-style arguments, minimum transid filtering, and an optional sector cap.
- `btrfs_auto_defrag_init()` and `btrfs_auto_defrag_exit()` manage the inode-defrag slab cache.
- `btrfs_add_inode_defrag()` queues an inode for autodefrag with an extent-size threshold.
- `btrfs_run_defrag_inodes()` drains queued autodefrag work.
- `btrfs_cleanup_defrag_inodes()` frees queued autodefrag records.
- `btrfs_defrag_root()` defragments B-tree leaves for a root.
- `btrfs_defrag_cancelled()` currently treats a pending signal on `current` as cancellation.

## Integration Points

This header is included by defrag implementation and external Btrfs code that schedules or invokes defrag work. It forward-declares filesystem, root, inode, transaction, readahead, and ioctl argument types to avoid broad include coupling.

## Invariants And Risks

- Cancellation semantics are signal-based and depend on the task running the defrag loop.
- Callers of `btrfs_defrag_file()` must provide a valid `file_ra_state`.
- Lifecycle callers must initialize the defrag cache before queueing inode records and destroy it only after queues are cleaned up.

## Testing Notes

Compile and lifecycle coverage should verify init/exit ordering, queue cleanup at unmount, cancellation propagation, and public caller behavior for file and root defrag entry points.
