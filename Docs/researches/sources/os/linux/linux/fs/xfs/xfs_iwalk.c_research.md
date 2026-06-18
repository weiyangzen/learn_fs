# File Research: sources/os/linux/linux/fs/xfs/xfs_iwalk.c

## Role
Implements inode and inode-btree record walkers for XFS. It iterates allocated inodes or raw inobt records in increasing inode order, starting from an inode cursor, with optional single-AG limitation and optional threaded per-AG execution.

## Main Structures and Entry Points
- `struct xfs_iwalk_ag` stores per-AG walk state, cached inobt records, callbacks, transaction/perag references, flags, and optional parallel work state.
- `xfs_iwalk` walks allocated inodes with a caller callback.
- `xfs_iwalk_threaded` queues one work item per allocation group for parallel inode walking.
- `xfs_inobt_walk` walks inobt records directly.
- Internal helpers allocate record caches, start btree cursors at the correct point, run callbacks safely, and compute prefetch sizes.

## Behavior
The walker reads inobt records under an AGI btree cursor but does not call arbitrary callbacks while holding cursor state. Instead it caches inobt records in memory, tears down the cursor and AGI buffer, runs callbacks over cached records, then recreates the cursor at the next inode record. This avoids holding btree state across callbacks that may perform filesystem operations.

For inode walks, free bits in each inobt record are used to skip free inodes, and allocated inode clusters are readaheaded before callbacks. When starting in the middle of a chunk, earlier bits are marked free so records are not returned twice. Empty records can be skipped for inode walks. The code detects non-forward cursor progress and marks the btree sick on corruption.

Threaded walking uses `xfs_pwork` to allocate per-AG work state, hold perag references for async execution, allocate an empty transaction per worker for recursive buffer locking, and support polling/abort.

## Interactions
Used by `xfs_itable.c` for bulkstat/inumbers and by other filesystem scans that need safe inode iteration. Depends on ialloc/inobt btree cursor APIs, perag iteration, inode buffer readahead, transaction buffer locking, health marking, and parallel work helpers.

## Invariants and Error Handling
- Callback return values propagate; `-ECANCELED` is reserved as a caller-controlled stop sentinel.
- Start flags are limited to `XFS_IWALK_SAME_AG`.
- Inobt record cache size is at least two records to simplify mid-record starts and cursor restart.
- Prefetch is capped to avoid excessive memory or readahead.
- Cursor and AGI buffer are always released through `xfs_iwalk_del_inobt`.
