# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.c

This file implements delayed inode and delayed directory index item handling. It batches inode item updates, inode ref deletion, and directory index insert/delete operations so they can be flushed later through transaction processing or async workers.

Core data model:
- A `btrfs_delayed_root` tracks global delayed nodes and item counts.
- A `btrfs_delayed_node` is per inode, cached in the inode and indexed by root xarray.
- Each delayed node owns two rbtrees:
  - `ins_root` for delayed directory index insertions.
  - `del_root` for delayed directory index deletions.
- Items are ordered by directory index offset and can also be temporarily linked into readdir/logging lists.

Initialization and lifetime:
- `btrfs_delayed_inode_init()` creates the delayed node slab cache.
- `btrfs_init_delayed_root()` initializes global counters, lock, waitqueue, and node lists.
- `btrfs_get_delayed_node()` retrieves an existing node from inode cache or root xarray, handling races with node removal via `refcount_inc_not_zero()`.
- `btrfs_get_or_create_delayed_node()` allocates, initializes, reserves xarray storage, and installs a node.
- `btrfs_release_delayed_node()` requeues or dequeues based on pending item count, drops the caller ref, erases from the xarray on final ref, and frees the slab object.

Delayed item handling:
- `btrfs_alloc_delayed_item()` creates variable-length delayed items with inline data.
- `__btrfs_add_delayed_item()` inserts into the insertion or deletion rbtree and increments delayed item counters.
- `btrfs_release_delayed_item()` removes an item from its rbtree if present and frees it on last ref.
- `finish_one_item()` decrements global delayed item count and wakes waiters when thresholds/batches are crossed.

Metadata reservation:
- Delayed item insertion metadata is migrated from the transaction reservation to `fs_info->delayed_block_rsv`.
- Deletion items track `bytes_reserved` per item.
- Insertion items instead track reserved leaves in the delayed node using `index_item_leaves` and `curr_index_batch_size`.
- Delayed inode updates reserve one metadata update unit and track it in `node->bytes_reserved`.
- Release paths either free qgroup metadata or convert it depending on whether cleanup is error-like or normal transaction conversion.

Flush path:
- `btrfs_insert_delayed_item()` batches consecutive dir index insertion items into one leaf-sized insert where possible.
- During log replay, batching is restricted to continuous keys only.
- `btrfs_delete_delayed_items()` looks up delayed deletion keys and batch-deletes consecutive matching items from the leaf.
- `__btrfs_update_delayed_inode()` writes the delayed inode item to the tree and optionally deletes the final inode ref/extref for delayed iref deletion.
- `__btrfs_commit_inode_delayed_items()` runs insertions, deletions, records the root in the transaction, then updates the inode.
- `btrfs_run_delayed_items()` and `btrfs_run_delayed_items_nr()` flush global delayed nodes with `fs_info->delayed_block_rsv`.
- `btrfs_commit_inode_delayed_items()` flushes one inode’s delayed node.
- `btrfs_commit_inode_delayed_inode()` commits only the delayed inode item for eviction-style paths.

Async balancing:
- Thresholds:
  - `BTRFS_DELAYED_BACKGROUND` = 128
  - `BTRFS_DELAYED_WRITEBACK` = 512
  - `BTRFS_DELAYED_BATCH` = 16
- `btrfs_balance_delayed_items()` queues background work when pending delayed items exceed thresholds.
- `btrfs_async_run_delayed_root()` joins transactions and drains prepared delayed nodes from worker context.
- Waiters are woken using `items_seq` and delayed item count thresholds.

Directory index operations:
- `btrfs_insert_delayed_dir_index()` builds an inline `btrfs_dir_item`, inserts it into the node’s insertion rbtree, and reserves/reuses delayed item leaf metadata.
- `btrfs_delete_delayed_dir_index()` first tries to remove a not-yet-flushed insertion; otherwise it creates a deletion item.
- `btrfs_inode_delayed_dir_index_count()` copies the delayed node index counter back to the inode.

Readdir support:
- `btrfs_readdir_get_delayed_items()` collects delayed insertions and deletions up to a last index, taking extra item refs.
- It upgrades the inode lock from shared to exclusive to serialize use of `readdir_list`.
- `btrfs_readdir_delayed_dir_index()` emits delayed insertion items through `dir_emit()`.
- `btrfs_should_delete_dir_index()` checks whether an on-disk index should be suppressed by a delayed deletion.
- `btrfs_readdir_put_delayed_items()` drops item refs and downgrades the inode lock back to shared.

Delayed inode content:
- `fill_stack_inode_item()` snapshots VFS/Btrfs inode metadata into a stack-format inode item.
- `btrfs_fill_inode()` restores inode fields from a dirty delayed inode item if present.
- `btrfs_delayed_update_inode()` creates or updates delayed inode state and increments global delayed item accounting.
- `btrfs_delayed_delete_inode_ref()` marks final inode ref deletion for async handling, except during log recovery.

Cleanup:
- `__btrfs_kill_delayed_node()` removes pending insertion/deletion items, releases metadata, clears delayed inode/iref state.
- `btrfs_kill_delayed_inode_items()` handles one inode.
- `btrfs_kill_all_delayed_nodes()` walks the root xarray in batches and kills all nodes.
- `btrfs_destroy_delayed_inodes()` drains all delayed nodes from fs shutdown/transaction cleanup.
- `btrfs_assert_delayed_root_empty()` warns if delayed nodes remain.

Logging support:
- `btrfs_log_get_delayed_items()` gathers delayed items for directory logging, skipping already logged/listed items.
- `btrfs_log_put_delayed_items()` marks gathered items as logged and drops refs.
- These functions deliberately avoid normal node release/requeue semantics because logging is not mutating delayed item state.

Important locking:
- Root delayed lists use `delayed_root->lock`.
- Per-node rbtrees and dirty inode state use `delayed_node->mutex`.
- The root xarray uses `xa_lock`.
- The code avoids holding tree paths while releasing delayed nodes to prevent lock ordering deadlocks.
