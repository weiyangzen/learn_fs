# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.c

This file implements generic inode and inode-btree walking for XFS. It supports single-threaded inode iteration, threaded per-AG inode iteration, and raw inobt record iteration.

Core model:
- `struct xfs_iwalk_ag` tracks one AG walk: mount, transaction, perag, start inode, last inode, cached inobt records, callbacks, caller data, and behavior flags.
- The walker reads inode btree records into an in-memory cache, drops btree cursor/AGI state before invoking callbacks, then reconstructs cursor state afterward. This allows callbacks to perform arbitrary work without holding inobt cursor or AGI locks.

Key helpers:
- `xfs_iwalk_ichunk_ra` performs inode-cluster readahead for allocated inodes in an inobt record.
- `xfs_iwalk_adjust_start` marks inodes before the requested start agino as free to support restarting inside a chunk.
- `xfs_iwalk_alloc` / `xfs_iwalk_free` manage cached record arrays.
- `xfs_iwalk_ag_recs` invokes inobt-record callbacks and inode callbacks for allocated inodes.
- `xfs_iwalk_del_inobt` tears down btree cursor and releases AGI buffer.
- `xfs_iwalk_ag_start` positions the cursor at the start point and handles mid-record start trimming.
- `xfs_iwalk_run_callbacks` drops cursor/AGI, optionally drops the empty transaction, runs callbacks, clears cache, recreates cursor, and resumes from the next agino.
- `xfs_iwalk_ag` walks all relevant records in one AG, ensures monotonic progress, skips empty records when configured, triggers readahead, and runs cached callbacks.

Public inode walk:
- `xfs_iwalk` walks allocated inodes from `startino` with optional `XFS_IWALK_SAME_AG`.
- It uses an empty transaction supplied by the caller, trims the start record, skips empty records, and prefetches based on requested inode count.

Threaded inode walk:
- `xfs_iwalk_threaded` queues one work item per AG using `xfs_pwork`.
- `xfs_iwalk_ag_work` allocates per-work state, creates an empty transaction, walks its AG, cancels the transaction, frees resources, and drops the perag reference.
- Optional polling is supported.

Inobt record walk:
- `xfs_inobt_walk` walks inode btree records instead of individual inodes.
- It uses `xfs_inobt_walk_prefetch`, capped to a page of records and with a minimum of two records.

Flags:
- `XFS_IWALK_SAME_AG` limits walking to the AG containing `startino`.

Risk notes:
- Correctness depends on preserving cursor progress across callback execution while avoiding stale lock state.
- The monotonic `lastino` check marks the btree sick and returns corruption if records go backwards.
- Callback return `-ECANCELED` is intentionally supported as a non-error stop signal for users such as bulkstat.
