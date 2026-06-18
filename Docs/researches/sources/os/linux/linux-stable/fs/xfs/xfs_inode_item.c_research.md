# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.c

## Purpose

Implements XFS inode log items: precommit synchronization, log vector sizing/formatting, pin/unpin behavior, AIL push support, commit sequence tracking, inode flush completion, flush abort, and old-format conversion.

## Main Responsibilities

- Defines `xfs_ili_cache` for `struct xfs_inode_log_item`.
- Provides `xfs_inode_item_ops` for transaction/log integration.
- Converts incore inode state into log dinode records and fork payload vectors.
- Coordinates dirty fields, last-flushed fields, flush LSNs, and buffer attachment.
- Tracks commit sequence numbers for fsync and datasync optimization.
- Handles inode log item pin/unpin and AIL push behavior.
- Completes inode buffer I/O by deleting flushed items from the AIL and clearing flush state.
- Aborts inode flush state during stale inode cleanup or shutdown.
- Converts 32-bit inode log format records to native format for recovery.

## Precommit Flow

`xfs_inode_item_precommit` runs before final transaction logging:

- Clears lazy timestamp dirty state from the VFS inode.
- Upgrades eligible inodes to bigtime format.
- Fixes invalid realtime inherited extent-size hints.
- Reads and attaches the inode cluster buffer to the log item if needed.
- Sets `ili_dirty_flags` and merges new logged fields with `ili_last_fields`.
- Converts iversion logging into core inode logging.
- Optionally verifies the generated dinode under expensive debug checks.

The sort key is inode number so precommit buffer locking happens in stable order.

## Formatting Flow

- `xfs_inode_item_size` accounts for format, core, and optional data/attr fork vectors.
- `xfs_inode_item_format_data_fork` formats extent arrays, btree roots, local data, or device payloads according to data fork format.
- `xfs_inode_item_format_attr_fork` formats attr fork extent arrays, btree roots, or local attr data.
- `xfs_inode_to_log_dinode` translates incore/VFS inode fields into the log dinode, including timestamps, owner ids, nlink, generation, size, blocks, flags, metatype, UUID, CRC placeholders, and extent counters.
- `xfs_inode_item_format` emits the format record, core record, and fork payloads, then updates the exact logged field mask.

## Pin, Push, and Commit Semantics

- `xfs_inode_item_pin` increments `i_pincount`.
- `xfs_inode_item_unpin` decrements the pin count, clears commit/datasync sequences at zero, and wakes waiters.
- `xfs_inode_item_push` tries to flush the inode cluster buffer from the AIL unless pinned, stale, locked, or already flushing.
- `xfs_inode_item_committed` skips AIL insertion for stale inodes and unpins directly.
- `xfs_inode_item_committing` records commit sequence numbers and only records datasync sequence numbers for changes beyond iversion/timestamp-only updates.
- `xfs_inode_item_release` unlocks inode locks held by the transaction item.

## Flush Completion and Abort

- `xfs_buf_inode_iodone` walks inode log items attached to an inode buffer, handles stale inodes, batches AIL updates, and finishes flush state.
- `xfs_iflush_ail_updates` deletes successfully flushed inode items from the AIL if their LSN has not changed.
- `xfs_iflush_finish` detaches clean inodes from the buffer, clears `ili_last_fields`, `ili_flush_lsn`, `XFS_LI_FLUSHING`, and `XFS_IFLUSHING`.
- `xfs_iflush_abort` removes an inode item from the AIL and clears buffer/field state while the cluster buffer is locked.
- `xfs_iflush_shutdown_abort` safely locks the cluster buffer from arbitrary shutdown context before aborting.

## Important Invariants

- Inode cluster buffer attachment is delayed until precommit to preserve AGI/AGF/buffer lock ordering.
- Inode fork logged size reflects current fork size, not the largest previous relogged size.
- Dirty inode fields cannot be forgotten until the backing inode buffer I/O completes; `ili_last_fields` preserves this relationship.
- A stale inode item must not be inserted into the AIL after its cluster buffer is freed.
- The inode log item may hold a buffer reference while attached to `bp->b_li_list`; cleanup must drop that reference exactly once.

## Dependencies

Uses transaction/log item infrastructure, buffer log item lists, AIL operations, inode fork conversion helpers, dinode verifiers, timestamp/iversion helpers, realtime bitmap include context, and shutdown/error handling.

## Research Notes

This file is the bridge between incore inode mutation and journal durability. The subtle logic is the three-way coordination among transaction commit, inode flush, and buffer I/O completion, especially when inodes are relogged while a previous flush is still outstanding.
