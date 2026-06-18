# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.h

## Purpose
Declares the in-core buffer log item structure, buffer log item flags, and public helpers used by XFS transaction, buffer, quota, inode, and recovery code.

## Main Types and Flags
`struct xfs_buf_log_item` embeds the common `xfs_log_item`, points to the backing `xfs_buf`, tracks BLI flags, recursion/reference counts, and stores one or more `xfs_buf_log_format` records. A single embedded format is used for common one-map buffers; multi-map buffers use a dynamically allocated array.

Flags record hold/dirty/stale/logged state plus inode allocation, stale inode, inode buffer, and ordered-buffer semantics.

## Public API
Declares initialization, completion, reference release, dirty range logging, dirty-format testing, inode/dquot/buffer I/O completion hooks, log iovec validation, and invalidation log-space estimation.

## Dependencies and Configuration
`xfs_buf_dquot_iodone` is compiled as a no-op without `CONFIG_XFS_QUOTA`. The header is kernel-only and depends on log-format and buffer definitions supplied by including translation units.
