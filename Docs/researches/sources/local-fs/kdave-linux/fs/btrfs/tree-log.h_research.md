# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-log.h

## Purpose

`tree-log.h` declares the public interface and shared context for Btrfs tree logging implemented in `tree-log.c`. It is included by Btrfs code that needs to log fsync state, update logs after namespace changes, recover logs at mount, or free log roots at transaction commit.

## Key Constants

`BTRFS_NO_LOG_SYNC` is a positive sentinel return value from `btrfs_log_dentry_safe()` indicating that no log sync is needed.

`BTRFS_LOG_FORCE_COMMIT` is a negative sentinel outside normal errno space. It means tree logging is unsafe or impossible and the caller must force a full transaction commit. It is negative so it can propagate through paths that treat negative values as failure/full-sync conditions.

## `struct btrfs_log_ctx`

`btrfs_log_ctx` is per logging operation and tracks both result state and work discovered during logging.

Fields include:

- `log_ret`: result propagated to waiters after log commit.
- `log_transid`: log transaction joined by this context.
- `log_new_dentries`: set when logging a directory found new dentries whose target inodes must also be logged.
- `logging_new_name`: set when logging due to link/rename new-name update.
- `logging_new_delayed_dentries`: recursion guard for delayed dentry logging.
- `logged_before`: whether the inode was already logged in the current transaction.
- `inode`: inode associated with this context.
- `list`: entry in root log context wait lists.
- `ordered_extents`: ordered extents relevant to fast fsync.
- `conflict_inodes`: inodes discovered as name/reference conflicts that need logging.
- `num_conflict_inodes`: cap enforcement for conflict logging.
- `logging_conflict_inodes`: recursion guard for conflict inode logging.
- `scratch_eb`: reusable cloned extent buffer used while copying subvolume tree leaves into the log tree.

## Inline Helpers

`btrfs_set_log_full_commit()` stores the current transaction ID in `fs_info->last_trans_log_full_commit`, marking tree logging unsafe for that transaction.

`btrfs_need_log_full_commit()` checks whether the current transaction has been marked for full commit fallback.

## Exported API

Initialization and cleanup:

- `btrfs_init_log_ctx()`
- `btrfs_init_log_ctx_scratch_eb()`
- `btrfs_release_log_ctx_extents()`

Log commit/free/recovery:

- `btrfs_sync_log()`
- `btrfs_free_log()`
- `btrfs_free_log_root_tree()`
- `btrfs_recover_log_trees()`

Fsync entry point:

- `btrfs_log_dentry_safe()`

Namespace/log mutation helpers:

- `btrfs_del_dir_entries_in_log()`
- `btrfs_del_inode_ref_in_log()`
- `btrfs_record_unlink_dir()`
- `btrfs_record_snapshot_destroy()`
- `btrfs_record_new_subvolume()`
- `btrfs_log_new_name()`

Log transaction lifetime helpers:

- `btrfs_end_log_trans()`
- `btrfs_pin_log_trans()`

## Research Notes

The header intentionally exposes only the coordination surface needed outside `tree-log.c`. Most policy and replay logic remains private in the C file, while callers receive a compact API for fsync logging, log lifecycle, and correctness hooks around unlink, rename, snapshot deletion, and subvolume creation.
