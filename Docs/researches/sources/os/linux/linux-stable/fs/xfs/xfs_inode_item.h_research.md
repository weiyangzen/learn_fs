# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item.h

## Purpose

Declares the XFS inode log item structure and the helper API for inode log item lifecycle, flush abort, and recovery-format conversion.

## Main Types

- `struct xfs_inode_log_item`
  - Embeds `struct xfs_log_item`.
  - Points back to the owning `struct xfs_inode`.
  - Tracks transaction-held inode lock flags and dirty flags.
  - Uses `ili_lock` to serialize dirty/flush state.
  - Tracks last flushed fields, current fields, flush LSN, commit sequence, and datasync sequence.

## Main API

- `xfs_inode_clean`
- `xfs_inode_item_init`
- `xfs_inode_item_destroy`
- `xfs_iflush_abort`
- `xfs_iflush_shutdown_abort`
- `xfs_inode_item_format_convert`
- `xfs_ili_cache`

## Important Invariants

- `ili_lock` protects interactions between dirty state and flush state because inode dirtying, flushing, and completion use different inode lock combinations.
- `ili_commit_seq` and `ili_datasync_seq` allow fsync/fdatasync paths to decide whether a log force is needed without checking pin state under ILOCK.
- `xfs_inode_clean` treats an inode without an item, or with no logged dirty fields, as clean.

## Research Notes

This header is the state contract consumed by transaction code, inode flush code, and fsync/log-force paths. The fields are intentionally fine-grained because correctness depends on distinguishing current dirty fields from fields already copied to an inode buffer but not yet durable.
