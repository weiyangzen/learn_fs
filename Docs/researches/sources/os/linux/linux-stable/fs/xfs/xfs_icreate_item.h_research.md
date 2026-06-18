# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icreate_item.h

## Purpose

Declares the in-memory inode-create log item and its transaction helper.

## Main Types

- `struct xfs_icreate_item`
  - Embeds `struct xfs_log_item`.
  - Carries an `xfs_icreate_log` format record.

## Main API

- `xfs_icreate_cache`
- `xfs_icreate_log`

## Important Invariants

- The header exposes only the constructor/logging helper; formatting and recovery are private to the `.c` file.
- The logged fields describe a newly allocated inode chunk by AG-relative start, count, inode size, extent length, and generation.

## Research Notes

This is a small transaction-log interface used by inode allocation code to make bulk inode initialization crash recoverable.
