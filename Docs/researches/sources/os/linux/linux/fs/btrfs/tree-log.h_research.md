# File Research: sources/os/linux/linux/fs/btrfs/tree-log.h

Public Btrfs tree-log interface. This header defines the log context used across fsync/logging paths, the special log return values, and the exported helpers for syncing, replaying, freeing, pinning, and updating tree logs.

Key responsibilities:
- Defines `BTRFS_NO_LOG_SYNC`, meaning the inode was already safely logged and no log sync is required.
- Defines `BTRFS_LOG_FORCE_COMMIT`, the sentinel that forces callers to commit the whole transaction instead of relying on the tree log.
- Defines `struct btrfs_log_ctx`, which carries per-fsync logging result, log transaction id, inode pointer, ordered extents, conflict inode tracking, recursive logging flags, and reusable scratch extent buffer.
- Provides helpers to initialize log contexts, allocate scratch buffers for expensive item-copy logging, and release ordered extents held by a context.
- Provides inline full-commit flag helpers through `last_trans_log_full_commit`.
- Declares log sync, log freeing, log-root-tree freeing, mount-time log replay, safe dentry logging, log dentry/ref deletion, log transaction pin/end, unlink/snapshot/subvolume recording, and new-name logging APIs.

Important fields:
- `log_ret` and `log_transid` carry the result and id observed by tasks sharing a log commit.
- `log_new_dentries`, `logging_new_name`, and `logging_new_delayed_dentries` control recursive logging of new names and delayed directory entries.
- `logged_before` caches whether the target inode was already logged in the current transaction.
- `ordered_extents` keeps ordered extents whose checksums/state are needed for fsync correctness.
- `conflict_inodes`, `num_conflict_inodes`, and `logging_conflict_inodes` bound and control recursive conflict-inode logging.
- `scratch_eb` is a reusable cloned/dummy extent buffer used to avoid allocation and lock-order problems while copying tree items into the log.

Dependencies:
- Includes Linux list, VFS, fscrypt, and Btrfs transaction definitions.
- Forward-declares VFS dentries/inodes, ordered extents, roots, and transaction handles.

Important invariants:
- `btrfs_set_log_full_commit()` and `btrfs_need_log_full_commit()` are transaction-scoped via `trans->transid`.
- `BTRFS_LOG_FORCE_COMMIT` is deliberately negative so generic error-style propagation marks the log unusable for fast sync.
- Context ordered extents must be released by callers after logging completes or aborts.
- Log pin/end calls must be balanced to avoid either premature log sync or permanently blocked log commits.
- Callers using name/ref deletion helpers must already be in the correct transaction and satisfy the locking contracts established by `tree-log.c`.

Notable risks:
- Misinterpreting `BTRFS_NO_LOG_SYNC` as ordinary success that still needs sync would add unnecessary work; misinterpreting `BTRFS_LOG_FORCE_COMMIT` as a normal error could skip the required full commit fallback.
- `struct btrfs_log_ctx` is shared across recursive logging paths, so flag restoration and conflict list cleanup are essential.
- The header exposes low-level log mutation functions whose safety depends on precise ordering around rename, unlink, snapshot deletion, and subvolume creation.
