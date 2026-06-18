# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_buf.c

## Purpose

Implements transaction integration for XFS metadata buffers. It joins buffers to transactions, tracks logged byte ranges, manages buffer recursion/holds, and marks buffer log items for recovery.

## Main Responsibilities

- Finds buffers already attached to a transaction.
- Gets, reads, locks, and joins buffers to transactions.
- Handles superblock and realtime superblock buffer joins.
- Releases or forcibly detaches clean buffers from transactions.
- Marks buffers dirty, stale, ordered, inode-buffer, inode-allocation-buffer, or dquot-buffer.
- Logs byte ranges through buffer log items.
- Assigns buffer type metadata for log recovery.

## Important Invariants

- Joined buffers must be locked and have a valid buffer log item.
- Recursive buffer lookups increment `bli_recur` instead of relocking.
- Dirty or stale buffers remain attached until transaction commit/cancel.
- Stale buffers set cancel flags so recovery ignores older logged copies.
- Ordered buffers cannot already have dirty logged format ranges.
- Buffer type flags are recovery-facing and must match the on-disk metadata contents.

## Dependencies

Uses XFS buffer cache, buffer log item code, transaction item lists, verifier ops, shutdown handling, and recovery buffer type definitions.

## Research Notes

The high-risk logic is around buffer lifetime and state transitions: recursion counts, stale cancellation, ordered-buffer semantics, and verifier failure shutdown behavior.
