# File Research: sources/os/linux/linux-stable/fs/nilfs2/ioctl.c

## Summary
Implements NILFS ioctl and file-attribute operations. It exposes checkpoint, segment, DAT, cleaner, resize, trim, sync, allocation-range, and filesystem-label controls to userspace.

## Main Responsibilities
- Copies vector-style metadata requests between userspace and kernel buffers.
- Gets/sets visible file attributes.
- Returns inode generation numbers.
- Changes checkpoint/snapshot mode and deletes checkpoints.
- Retrieves checkpoint, segment usage, DAT virtual block, and disk block descriptor information.
- Moves blocks and prepares cleaner garbage-collection work.
- Frees virtual blocks and marks live GC target blocks dirty.
- Runs segment cleaning.
- Forces checkpoint creation and device flush.
- Resizes the filesystem, trims free segments, sets allocation range, and gets/sets fs labels.
- Dispatches native and compat ioctl commands.

## Important Behavior
`nilfs_ioctl_wrap_copy()` processes `nilfs_argv` requests in page-sized chunks, validates item size and index overflow, optionally copies input records from userspace, calls a metadata callback, optionally copies output records back, and returns the number of processed members through `v_nmembs`.

Mutating checkpoint, segment usage, cleaner, resize, and label operations require `CAP_SYS_ADMIN` where appropriate and acquire write access with `mnt_want_write_file()`. Checkpoint mode changes are serialized with `ns_snapshot_mount_mutex` to avoid races with snapshot mounts.

Cleaner support is split into metadata queries and active cleaning. `nilfs_ioctl_move_blocks()` groups virtual descriptors by inode/checkpoint, obtains GC inodes, queues source data/node buffers, waits for reads, validates node buffers, marks buffers dirty, and leaves GC inodes on `ns_gc_inodes` until cleanup. `nilfs_ioctl_prepare_clean_segments()` deletes old checkpoints, frees virtual blocks, and marks live DAT or B-tree blocks dirty before `nilfs_clean_segments()` writes moved blocks.

`nilfs_ioctl_clean_segments()` validates all five cleaner argument vectors, bounds counts by the number of blocks in the target segments, copies user arrays, enforces single cleaner execution with `THE_NILFS_GC_RUNNING`, runs move/clean, removes GC inodes, and frees all temporary buffers.

Read-only information ioctls use `ns_segctor_sem` around cpfile/sufile/dat/bmap access. `FITRIM` validates discard support and adjusts `minlen` to device granularity before calling sufile trim. Label setting updates both superblocks when present under `ns_sem`.

## Risks
Cleaner ioctls have many cross-checked user-provided arrays; validation of sizes, counts, and block liveness is central to safety. GC uses buffer association lists to detect conflicts. `nilfs_ioctl_wrap_copy()` relies on callbacks advancing positions correctly or falls back to incrementing by the batch size.
