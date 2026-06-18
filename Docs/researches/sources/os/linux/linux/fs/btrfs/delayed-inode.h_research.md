# File Research: sources/os/linux/linux/fs/btrfs/delayed-inode.h

This header defines the delayed inode and delayed directory item structures and exports their public API.

Key structures and flags:
- `enum btrfs_delayed_item_type` distinguishes delayed insertion and delayed deletion items.
- `struct btrfs_delayed_node` identifies an inode by `inode_id` and `root`, stores per-node counters and flags, owns insertion/deletion rbtrees, carries prepared/global list links, caches a stack-format inode item, and tracks delayed insertion leaf reservations.
- `struct btrfs_delayed_item` contains an rbtree node, directory index offset, batch/readdir/log list links, optional metadata reservation, parent delayed node, refcount, type, logged flag, data length, and flexible inline data.
- Node flags are `BTRFS_DELAYED_NODE_IN_LIST`, `BTRFS_DELAYED_NODE_INODE_DIRTY`, and `BTRFS_DELAYED_NODE_DEL_IREF`.

Exported functionality:
- Root/node lifecycle and cleanup: `btrfs_init_delayed_root()`, `btrfs_remove_delayed_node()`, `btrfs_kill_delayed_inode_items()`, `btrfs_kill_all_delayed_nodes()`, and `btrfs_destroy_delayed_inodes()`.
- Directory index staging: `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, and `btrfs_inode_delayed_dir_index_count()`.
- Flush and balance: `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_balance_delayed_items()`, and `btrfs_commit_inode_delayed_items()`.
- Inode item staging: `btrfs_delayed_update_inode()`, `btrfs_fill_inode()`, `btrfs_delayed_delete_inode_ref()`, and `btrfs_commit_inode_delayed_inode()`.
- Readdir helpers: delayed item collection, release, delete filtering, and delayed insertion emission.
- Directory logging helpers: `btrfs_log_get_delayed_items()` and `btrfs_log_put_delayed_items()`.
- Module lifecycle: `btrfs_delayed_inode_init()` and `btrfs_delayed_inode_exit()`.

Debug support:
- With `CONFIG_BTRFS_DEBUG`, delayed node references are tracked through `ref_tracker`.
- Without debug tracking, the helper functions compile to no-ops and return success.
