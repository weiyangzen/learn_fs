# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.c

## Purpose

Implements the XFS inode-create log item, which logs initialization of newly allocated inode chunks and replays that initialization during log recovery.

## Main Responsibilities

- Defines `xfs_icreate_cache` for `struct xfs_icreate_item` allocation.
- Provides log item operations for sizing, formatting, and release.
- Implements `xfs_icreate_log` to attach a dirty inode-create item to a transaction.
- Implements recovery ordering and pass2 replay for `XFS_LI_ICREATE` items.

## Key Data Flow

`xfs_icreate_log` records:

- allocation group number
- AG block number
- inode count
- inode size
- allocation extent length
- generation number

The item is formatted as a single `XLOG_REG_TYPE_ICREATE` vector. During recovery, `xlog_recover_icreate_commit_pass2` validates the record, checks for cancelled inode cluster buffers, and calls `xfs_ialloc_inode_init` to stamp initialized inode buffers.

## Important Invariants

- The log item has exactly one vector.
- The AG number, AG block number, inode size, inode count, and allocation length must match current filesystem geometry.
- The chunk length must be either a full inode allocation or the supported sparse minimum allocation.
- The inode count must be consistent with the extent length.
- ICREATE recovery is ordered with buffer-list recovery because it is logically equivalent to replaying initialized inode allocation buffers.
- If any cluster buffer was cancelled, replay is skipped conservatively; partial cancellation triggers a warning.

## Dependencies

Uses XFS transaction/log item infrastructure, log recovery reorder hooks, inode allocation geometry, cancellation tracking, and inode-buffer initialization.

## Research Notes

This file keeps inode chunk initialization recoverable without logging every initialized inode buffer directly. Its validation path is intentionally strict because malformed icreate records can otherwise initialize arbitrary inode buffers during recovery.
