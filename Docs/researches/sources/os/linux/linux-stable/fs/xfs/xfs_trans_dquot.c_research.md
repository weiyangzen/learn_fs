# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_dquot.c

## Purpose

Implements transactional quota accounting for XFS dquots. It records quota deltas in transactions, reserves quota resources, applies committed changes, and unwinds reservations on abort.

## Main Responsibilities

- Joins locked dquots to transactions and marks them dirty.
- Duplicates quota reservation state across rolling transactions.
- Tracks per-transaction block, realtime block, inode, delayed allocation, and reservation deltas.
- Applies dquot deltas at commit time.
- Releases reservations when transactions abort.
- Checks hard/soft quota limits and emits quota warnings.
- Reserves quotas by dquot set, by inode blocks, and for inode creation.
- Supports live quota hooks for online checking when configured.

## Important Invariants

- Per-transaction dquot arrays are sequential, not sparse.
- Dquots are locked before committed counter updates.
- Reservation counters must never fall below actual usage counters.
- User, group, and project quota reservations follow all-or-nothing unwind semantics.
- Project quota fatal reservation failures return `-ENOSPC`; user/group generally return `-EDQUOT`.
- Live hook installation/removal order preserves complete update sequences.

## Dependencies

Uses XFS quota manager, dquot locks, transaction item handling, health marking, warning delivery, live hooks, and quota default limit/timer adjustment.

## Research Notes

This file is the transactional boundary for quota consistency. The subtle parts are reservation carry-forward, delayed allocation accounting, and rollback after partial multi-dquot reservation failure.
