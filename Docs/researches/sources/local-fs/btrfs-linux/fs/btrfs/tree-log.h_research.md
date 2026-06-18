# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-log.h

## Purpose

`tree-log.h` declares the public interface for Btrfs tree logging. It exposes the fsync log context, log commit/recovery functions, log cleanup functions, and helper hooks used by unlink, rename, link, snapshot, and subvolume creation paths.

## Constants

`BTRFS_NO_LOG_SYNC` is a special positive return value from `btrfs_log_dentry_safe()` meaning no log sync is needed.

`BTRFS_LOG_FORCE_COMMIT` is a special negative value outside the normal errno range. It means tree logging cannot safely represent the operation and the caller must force a full transaction commit. The negative value is intentional because internal logging helpers often distinguish errors, false, true, and full-commit fallback.

## `struct btrfs_log_ctx`

`btrfs_log_ctx` is the per-logging-operation context shared across tree-log functions. It tracks:
- `log_ret` and `log_transid` for log commit participation.
- Whether new dentries, new names, or delayed dentries are being logged.
- Whether the inode was logged earlier in the transaction.
- The primary inode being logged.
- List linkage for root log context wait/commit lists.
- Ordered extents for fast fsync.
- Conflicting inodes discovered while logging references.
- Recursion guards for conflicting-inode logging.
- Optional `scratch_eb` used to clone source leaves and avoid lock-ordering/allocation deadlocks.

The fields mirror the concerns in `tree-log.c`: fsync batching, fast extent logging, recursive directory/new-name logging, and conflict repair.

## Declared Lifecycle Helpers

The header declares:
- `btrfs_init_log_ctx()`
- `btrfs_init_log_ctx_scratch_eb()`
- `btrfs_release_log_ctx_extents()`

These initialize logging contexts, optionally allocate reusable scratch extent buffers, and release ordered extents collected for fast fsync.

## Full-Commit Flag Helpers

Two inline helpers operate on `fs_info->last_trans_log_full_commit`:
- `btrfs_set_log_full_commit()`
- `btrfs_need_log_full_commit()`

They mark or test whether the current transaction must avoid tree-log commit and use a full transaction commit instead.

## Public Tree Log Operations

The header exposes:
- `btrfs_sync_log()` to write and commit a root’s log tree.
- `btrfs_free_log()` to free a root’s log tree.
- `btrfs_free_log_root_tree()` to free the global tree of log roots.
- `btrfs_recover_log_trees()` to replay logs during mount recovery.
- `btrfs_log_dentry_safe()` to log a dentry for fsync.

These are the main integration points with transaction commit, mount recovery, and fsync paths.

## Directory and Reference Update Hooks

The header declares hooks used by metadata mutation paths:
- `btrfs_del_dir_entries_in_log()`
- `btrfs_del_inode_ref_in_log()`
- `btrfs_record_unlink_dir()`
- `btrfs_record_snapshot_destroy()`
- `btrfs_record_new_subvolume()`
- `btrfs_log_new_name()`

These functions keep an existing log consistent when names are removed, renamed, linked, or when snapshot/subvolume operations require full-commit fallback.

## Concurrency Hooks

`btrfs_end_log_trans()` and `btrfs_pin_log_trans()` are declared for code that must hold log commits open while updating log-related state. In `tree-log.c`, they operate on the root’s log writer count and wake waiters when the active writers drain.

## Research Notes

This header is small but important: it defines the boundary between the Btrfs tree-log implementation and the rest of the filesystem. The central abstraction is `btrfs_log_ctx`, while the most important semantic contract is that callers must respect `BTRFS_LOG_FORCE_COMMIT` as a correctness-preserving fallback when partial tree logging cannot safely represent the current transaction state.
