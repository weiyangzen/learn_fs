# File Research: sources/local-fs/btrfs-linux/fs/btrfs/delayed-inode.h

This header defines delayed inode/directory item data structures and exports the delayed inode API.

Key structures:
- `enum btrfs_delayed_item_type`
  - `BTRFS_DELAYED_INSERTION_ITEM`
  - `BTRFS_DELAYED_DELETION_ITEM`
- `struct btrfs_delayed_node`
  - Identifies one inode by `inode_id` and `root`.
  - Tracks pending item count, delayed inode bytes reserved, index counter, and flags.
  - Owns insertion/deletion rbtrees.
  - Has node/prepared list links for global flush queues.
  - Tracks insertion leaf reservation state with `curr_index_batch_size` and `index_item_leaves`.
  - Includes debug-only reference tracking fields.
- `struct btrfs_delayed_item`
  - Rbtree node plus directory index offset.
  - Temporary list links for batch tree operations, readdir, and logging.
  - Per-item metadata reservation for deletion items.
  - Type, logged flag, data length, and flexible inline data.

Flags:
- `BTRFS_DELAYED_NODE_IN_LIST`
- `BTRFS_DELAYED_NODE_INODE_DIRTY`
- `BTRFS_DELAYED_NODE_DEL_IREF`

Exported operations:
- Delayed root lifecycle: `btrfs_init_delayed_root()`.
- Directory index insert/delete/query: `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, `btrfs_inode_delayed_dir_index_count()`.
- Flush and balancing: `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_balance_delayed_items()`, `btrfs_commit_inode_delayed_items()`.
- Inode update/fill/ref deletion: `btrfs_delayed_update_inode()`, `btrfs_fill_inode()`, `btrfs_delayed_delete_inode_ref()`, `btrfs_commit_inode_delayed_inode()`.
- Cleanup: `btrfs_remove_delayed_node()`, `btrfs_kill_delayed_inode_items()`, `btrfs_kill_all_delayed_nodes()`, `btrfs_destroy_delayed_inodes()`.
- Readdir and log integration helpers.
- Slab lifecycle: `btrfs_delayed_inode_init()`, `btrfs_delayed_inode_exit()`.

Debug support:
- Under `CONFIG_BTRFS_DEBUG`, delayed node references can be tracked with `ref_tracker`.
- When debug tracking is disabled, the helpers compile to no-ops.
