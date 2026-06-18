# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.h

This header defines delayed inode and delayed directory-item data structures plus their public APIs.

Core structures:
- `enum btrfs_delayed_item_type`
  - `BTRFS_DELAYED_INSERTION_ITEM`
  - `BTRFS_DELAYED_DELETION_ITEM`
- `struct btrfs_delayed_node`
  - Per-inode delayed metadata node.
  - Tracks inode id, root, reserved bytes, insertion/deletion rbtrees, mutex, delayed inode item, refs, item count, directory index counter, list flags, batching state, and debug ref trackers.
- `struct btrfs_delayed_item`
  - Rbtree item for delayed directory index insertion/deletion.
  - Contains index key offset, tree/readdir/log list links, reserved bytes, parent delayed node, refcount, type, logged state, payload length, and flexible data payload.

Flags:
- `BTRFS_DELAYED_NODE_IN_LIST`
- `BTRFS_DELAYED_NODE_INODE_DIRTY`
- `BTRFS_DELAYED_NODE_DEL_IREF`

Public API:
- Initialization and teardown:
  - `btrfs_delayed_inode_init()`
  - `btrfs_delayed_inode_exit()`
  - `btrfs_init_delayed_root()`
- Directory index operations:
  - `btrfs_insert_delayed_dir_index()`
  - `btrfs_delete_delayed_dir_index()`
  - `btrfs_inode_delayed_dir_index_count()`
- Running delayed work:
  - `btrfs_run_delayed_items()`
  - `btrfs_run_delayed_items_nr()`
  - `btrfs_balance_delayed_items()`
  - `btrfs_commit_inode_delayed_items()`
  - `btrfs_commit_inode_delayed_inode()`
- Inode update/delete:
  - `btrfs_delayed_update_inode()`
  - `btrfs_fill_inode()`
  - `btrfs_delayed_delete_inode_ref()`
- Cleanup:
  - `btrfs_remove_delayed_node()`
  - `btrfs_kill_delayed_inode_items()`
  - `btrfs_kill_all_delayed_nodes()`
  - `btrfs_destroy_delayed_inodes()`
- Readdir/logging support:
  - `btrfs_readdir_get_delayed_items()`
  - `btrfs_readdir_put_delayed_items()`
  - `btrfs_should_delete_dir_index()`
  - `btrfs_readdir_delayed_dir_index()`
  - `btrfs_log_get_delayed_items()`
  - `btrfs_log_put_delayed_items()`

Debug support:
- Under `CONFIG_BTRFS_DEBUG`, delayed node reference tracker directories and references are allocated, freed, printed, and quarantined.
- Without debug config, tracker helpers compile to no-ops.

Role in Btrfs:
The header is the contract for deferred inode and directory-index metadata batching. It exposes enough state for transaction, inode eviction, readdir, and logging code while keeping implementation details in `delayed-inode.c`.
