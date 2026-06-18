# File Research: sources/os/linux/linux/fs/btrfs/delayed-inode.c

This file implements Btrfs delayed inode and delayed directory index handling. It batches inode item updates, inode ref deletion, and directory index insert/delete records so metadata changes can be flushed later under transaction context or by async workers.

Core data model:
- `btrfs_delayed_root` stores global delayed item counters, a node list, a prepared list, lock, and waitqueue.
- Each `btrfs_delayed_node` belongs to one inode/root pair and is cached both in the inode and in the root `delayed_nodes` xarray.
- A delayed node owns two cached rbtrees: `ins_root` for delayed directory index insertions and `del_root` for delayed deletions.
- `btrfs_delayed_item` stores a directory index offset, item type, refcount, list links for batch/readdir/logging paths, optional reserved bytes, and flexible inline item data.

Initialization and lifetime:
- `btrfs_delayed_inode_init()` and `btrfs_delayed_inode_exit()` manage the slab cache for delayed nodes.
- `btrfs_init_delayed_root()` initializes counters, list heads, lock, and waitqueue.
- `btrfs_get_delayed_node()` first tries the inode cache, then the root xarray, and handles races with final node removal via `refcount_inc_not_zero()`.
- `btrfs_get_or_create_delayed_node()` allocates a node, initializes it, reserves an xarray slot, and installs it if another task did not win the race.
- `btrfs_release_delayed_node()` requeues nodes with pending work, dequeues empty nodes, drops the caller reference, erases the xarray entry on final reference, and frees the node.

Delayed item operations:
- `__btrfs_add_delayed_item()` inserts an item into the insertion or deletion rbtree, updates the per-node count, and increments global delayed item count.
- `finish_one_item()` increments `items_seq`, decrements global item count, and wakes waiters when the background threshold or batch boundary is crossed.
- `btrfs_release_delayed_item()` removes the item from its rbtree if present and frees it when the refcount reaches zero.
- Insertions are batched by `btrfs_insert_delayed_item()` into a leaf-sized `btrfs_item_batch`; log replay restricts batching to continuous keys to preserve ordering.
- Deletions are batched by `btrfs_batch_delete_items()` when consecutive delayed deletion items match consecutive on-disk directory index items.

Metadata reservation:
- Delayed inode updates reserve one metadata update unit into `fs_info->delayed_block_rsv` and record it in `node->bytes_reserved`.
- Delayed deletion items reserve and store `item->bytes_reserved`.
- Delayed insertion items account by reserved leaves on the delayed node with `index_item_leaves` and `curr_index_batch_size`, because many items can share one leaf.
- `btrfs_release_dir_index_item_space()` returns unused transaction reservation when an insertion fits in an already-reserved delayed insertion leaf.

Flush and commit paths:
- `__btrfs_commit_inode_delayed_items()` inserts delayed index items, deletes delayed index items, records the root in the transaction, then updates the inode item.
- `__btrfs_update_delayed_inode()` writes the saved inode item and, when marked, deletes the final inode ref/extref.
- `btrfs_run_delayed_items()` and `btrfs_run_delayed_items_nr()` drain global delayed nodes with `fs_info->delayed_block_rsv` installed as the transaction block reserve.
- `btrfs_commit_inode_delayed_items()` flushes all delayed work for one inode.
- `btrfs_commit_inode_delayed_inode()` joins a transaction and commits only a dirty delayed inode item.

Directory integration:
- `btrfs_insert_delayed_dir_index()` builds an inline `btrfs_dir_item`, adds it to the insertion rbtree, and updates delayed leaf reservation accounting.
- `btrfs_delete_delayed_dir_index()` first removes a matching unflushed insertion; if none exists, it queues a delayed deletion item.
- `btrfs_inode_delayed_dir_index_count()` copies the delayed node index counter back to the inode.
- Readdir helpers collect insertion/deletion items up to a target index, emit delayed insertions with `dir_emit()`, suppress deleted on-disk indexes, and release temporary refs afterward.
- Directory logging helpers collect delayed items into log lists, skip already logged/listed entries, and mark them logged when the log path is done.

Async balancing and cleanup:
- Delayed item thresholds are `BTRFS_DELAYED_BACKGROUND` 128, `BTRFS_DELAYED_WRITEBACK` 512, and `BTRFS_DELAYED_BATCH` 16.
- `btrfs_balance_delayed_items()` queues async worker flushes and may wait when the writeback threshold is exceeded.
- `btrfs_async_run_delayed_root()` drains prepared delayed nodes from a workqueue by joining transactions.
- Cleanup helpers kill delayed items for one inode, one root, all roots, or filesystem shutdown, releasing metadata reservations and qgroup prealloc as appropriate.

Important locking:
- The root delayed node lists use `delayed_root->lock`.
- Per-node dirty inode state and rbtrees use `delayed_node->mutex`.
- The root xarray uses xarray locking.
- The code deliberately releases btree paths before releasing delayed nodes to avoid lock ordering deadlocks.
