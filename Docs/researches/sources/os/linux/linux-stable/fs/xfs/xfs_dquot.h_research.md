# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.h

## Purpose
Defines the in-core dquot data model, quota resource accounting structures, flush synchronization helpers, inline quota-state helpers, and dquot management APIs.

## Main Types
- `struct xfs_dquot_res` tracks reserved count, actual count, hard/soft limits, and timer/grace state for blocks, inodes, or realtime blocks.
- `struct xfs_dquot_pre` stores speculative preallocation watermarks and low-space thresholds.
- `struct xfs_dquot` stores identity, cache reference state, disk buffer location, block/inode/realtime resource counters, embedded dquot log item, preallocation thresholds, dquot lock, flush completion, pin count, and pin waitqueue.

## Inline Helpers
Provides resource limit checks, dquot flush lock/unlock primitives, type masking, per-type quota-on and enforcement checks, inode-to-dquot lookup, low-space detection, and `xfs_qm_dqhold`.

## Public API
Declares dquot read/get/release/flush/destruction, timer/default-limit adjustment, quota ID extraction from inodes, multi-dquot locking, preallocation setup, attached-buffer helpers, and dquot block initialization.

## Invariants
`q_flush` is a completion used as a single-access flush gate. Metadata inodes do not have attached dquots. `xfs_dquot_type` masks record flags such as bigtime from the base user/group/project type.
