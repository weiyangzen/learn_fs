# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_trans.c

## Overview
`ufs_trans.c` contains UFS transaction/logging glue. It wraps superblock and inode updates in transaction reservations, pushes logged deltas for buffers, inodes, quotas, and summary info, maintains debug metadata maps, estimates log reservations for writes/truncates, splits large operations, and triggers hard locks when logging errors occur.

## Main Responsibilities
- Hard-lock filesystems with errored logs via `ufs_trans_hlock()`.
- Wake the hlock thread with `ufs_trans_onerror()`.
- Transaction-wrap superblock updates, inode updates, and superblock writes.
- Push logged deltas for summary info, delayed buffers, inodes, directory blocks, and quotas.
- Maintain debug-only metadata maps for static and dynamic metadata regions.
- Calculate log space needed for writes and truncates.
- Split oversized truncate/write operations into log-sized chunks.

## Transaction Wrappers
- `ufs_trans_sbupdate()` wraps `sbupdate()` unless already in `T_DONTBLOCK`; it avoids logging work during panic on trans filesystems.
- `ufs_trans_iupdat()` wraps `ufs_iupdat()` under `i_contents` reader lock.
- `ufs_trans_sbwrite()` wraps `ufs_sbwrite()` under `vfs_lock`.
- `ufs_trans_itrunc()` runs non-logging truncates directly, but for logging filesystems reserves space, sets `T_DONTBLOCK`, and may loop over partial truncates.
- `ufs_trans_write()` performs chunked writes, ending and starting transactions between chunks while preserving the caller’s final end-of-transaction responsibility.

## Delta Push Paths
- `ufs_trans_push_si()` logs cylinder-group summary info from `fs_csp`.
- `ufs_trans_push_buf()` writes delayed-write buffers if still present, otherwise returns `ENOENT`.
- `ufs_trans_push_inode()` igets an inode and writes it if modified.
- `ufs_trans_dir()` maps a directory offset to a disk block and declares a `DT_DIR` delta.
- `ufs_trans_quota()` marks a dquot as participating in a transaction, takes an extra reference, and declares a quota delta.
- `ufs_trans_push_quota()` logs the quota record or cleans up on quota transaction cancellation/error.
- `ufs_trans_dqrele()` wraps dquot release in a quota transaction.

## Hard-Lock Error Handling
- `ufs_trans_hlock()` scans `ufs_instances`, marks errored trans filesystems as `UT_HLOCKING`, then attempts `LOCKFS_HLOCK`.
- If a filesystem is already error-locked and the fix-failure queue has active entries, it wakes `ufs_fix`.
- After each attempt, it restores `vfs_validfs` to `UT_MOUNTED` and retries as needed for busy or conflicting lockfs state.

## Log Reservation Logic
- `ufs_log_amt()` estimates log bytes for writes/truncates from cylinder group metadata, inode size, indirect block deltas, and estimated cylinder group count.
- `ufs_trans_trunc_resv()` computes truncation reservation and chunk size when a truncate would exceed `ufs_trans_max_resv`.
- `ufs_trans_write_resv()` limits write reservations by `ufs_trans_max_resid`, prefaults user pages before opening a transaction, and reports chunking needs.

## Debug Metadata Map
- Under `DEBUG`, `ufs_trans_mata_mount()` records static metadata regions: superblock, cylinder groups, inode tables, and existing metadata in inodes.
- `ufs_trans_mata_iget()` classifies directory, shadow, attribute-directory, quota, and indirect blocks as metadata.
- Allocation/free helpers add or remove metadata map regions.

## Locking and Safety
- Uses `ufsvfs_mutex` for global instance traversal.
- Uses `vfs_dqrwlock` for inode/quota access around iget and dquot operations.
- Uses dquot locks to protect `DQ_TRANS`, modification flags, and reference counts.
- Uses `T_DONTBLOCK` to prevent nested blocking transaction behavior.
- Explicitly avoids transaction logging during panic for active logging filesystems.

## Research Notes
This file is the adapter between ordinary UFS metadata operations and the logging subsystem. Correctness depends on accurate reservation estimates, matching dquot reference/flag cleanup, and not opening transactions in contexts where lockfs or panic handling cannot tolerate blocking.
