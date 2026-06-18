# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-log.h

## Purpose

`tree-log.h` declares the public interface and shared context structure for Btrfs tree logging. It is included by Btrfs code that starts fsync logging, syncs or pins log transactions, updates logs after namespace changes, records cases that require full commits, and runs mount-time log recovery.

## Public Constants

- `BTRFS_NO_LOG_SYNC` is a positive sentinel return value from `btrfs_log_dentry_safe()` meaning the inode was already logged and no log sync is needed.
- `BTRFS_LOG_FORCE_COMMIT` is a negative sentinel outside normal errno values. It means the tree log cannot safely represent the operation and callers must force a full transaction commit.

## Main Structure: `struct btrfs_log_ctx`

`btrfs_log_ctx` carries per-fsync/per-log-operation state:

- `log_ret`: result propagated to waiters after a log commit.
- `log_transid`: log transaction id joined by this context.
- `log_new_dentries`: set when directory logging discovers new dentries whose target inodes must also be logged.
- `logging_new_name`: distinguishes rename/link log updates from ordinary fsync logging.
- `logging_new_delayed_dentries`: recursion guard for logging delayed directory dentries.
- `logged_before`: records whether the target inode was already logged in the current transaction.
- `inode`: primary inode for this context.
- `list`: linkage into a root’s log context waiter list.
- `ordered_extents`: ordered extents tracked for fast fsync and checksum/logged-ordered coordination.
- `conflict_inodes`: list of inodes discovered through reference/name conflicts while logging.
- `num_conflict_inodes`: cap counter for `conflict_inodes`.
- `logging_conflict_inodes`: recursion guard for conflict logging.
- `scratch_eb`: reusable temporary extent buffer used when copying subvolume-tree leaves into the log tree.

## Inline Helpers

- `btrfs_set_log_full_commit()` stores the current transaction id into `fs_info->last_trans_log_full_commit`, marking this transaction as unsafe for further tree-log commits.
- `btrfs_need_log_full_commit()` checks whether the current transaction has been marked for full commit.

Both helpers use `READ_ONCE`/`WRITE_ONCE` because this flag is consulted by concurrent log writers and syncers.

## Declared Functions

Context lifecycle:

- `btrfs_init_log_ctx()`
- `btrfs_init_log_ctx_scratch_eb()`
- `btrfs_release_log_ctx_extents()`

Log sync and cleanup:

- `btrfs_sync_log()`
- `btrfs_free_log()`
- `btrfs_free_log_root_tree()`
- `btrfs_recover_log_trees()`

Logging entry point:

- `btrfs_log_dentry_safe()`

Live log updates for unlink/rename/link:

- `btrfs_del_dir_entries_in_log()`
- `btrfs_del_inode_ref_in_log()`
- `btrfs_log_new_name()`

Transaction pinning:

- `btrfs_end_log_trans()`
- `btrfs_pin_log_trans()`

Recording operations that affect future logging safety:

- `btrfs_record_unlink_dir()`
- `btrfs_record_snapshot_destroy()`
- `btrfs_record_new_subvolume()`

## Dependencies

The header includes:

- `<linux/list.h>` for list heads in `btrfs_log_ctx`.
- `<linux/fs.h>` for VFS inode/dentry-related types.
- `<linux/fscrypt.h>` for encrypted filename strings used in log update declarations.
- `"transaction.h"` for `struct btrfs_trans_handle` and transaction context.

It forward-declares several Btrfs and VFS structures to keep inclusion light.

## Relationship to `tree-log.c`

The header exposes only the operations needed by the rest of Btrfs. The heavy policy, replay engine, directory range logic, conflict handling, extent/checksum logging, and zoned-device sync behavior live in `tree-log.c`. The header’s main design role is to centralize the `btrfs_log_ctx` contract and the two sentinel return values that callers must interpret correctly.
