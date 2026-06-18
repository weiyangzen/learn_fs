# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.c

This file implements delayed inode and delayed directory-index item handling. It batches inode item updates and directory index insert/delete operations so metadata modifications can be deferred, merged, and flushed later through transaction or async worker paths.

Major concepts:
- A `btrfs_delayed_node` exists per inode and is cached in both the inode and root xarray.
- Delayed insertion and deletion items are stored in separate cached rbtrees by directory index.
- Dirty inode updates are stored in `node->inode_item`.
- Nodes are linked into global delayed-root lists for background processing.
- Ref tracking is optionally enabled under `CONFIG_BTRFS_DEBUG`.

Initialization:
- `btrfs_delayed_inode_init()` creates the delayed-node slab cache.
- `btrfs_delayed_inode_exit()` destroys it.
- `btrfs_init_delayed_root()` initializes counters, locks, wait queue, and node lists.

Delayed node lifetime:
- `btrfs_get_delayed_node()` looks up an existing node from the inode cache or root xarray and handles races with refcount zeroing.
- `btrfs_get_or_create_delayed_node()` allocates, initializes, reserves an xarray slot, and publishes a new node.
- `btrfs_release_delayed_node()` and `btrfs_release_prepared_delayed_node()` requeue or dequeue nodes depending on pending item count, then drop references.
- `btrfs_remove_delayed_node()` removes the inode-cache reference during eviction.

Delayed item management:
- `btrfs_alloc_delayed_item()` allocates flexible-array delayed items.
- `__btrfs_add_delayed_item()` inserts into insertion or deletion rbtree and increments global delayed item count.
- `__btrfs_remove_delayed_item()` removes from rbtree and decrements delayed item count.
- `finish_one_item()` updates item sequence and wakes waiters when thresholds are crossed.

Metadata reservation:
- `btrfs_delayed_item_reserve_metadata()` migrates transaction reservation into `fs_info->delayed_block_rsv`.
- `btrfs_delayed_item_release_metadata()` releases delayed-item metadata bytes.
- Insertions reserve by delayed-node leaf batches rather than per item.
- `btrfs_delayed_inode_reserve_metadata()` reserves or migrates metadata for delayed inode item updates.
- `btrfs_delayed_inode_release_metadata()` releases or converts qgroup metadata reservations.

Flushing delayed items:
- `btrfs_insert_delayed_item()` batches contiguous delayed directory index insertions into one leaf when possible.
- `btrfs_insert_delayed_items()` flushes all delayed insertion items for a node.
- `btrfs_batch_delete_items()` batches adjacent deletion items found in the same leaf.
- `btrfs_delete_delayed_items()` flushes all delayed deletion items for a node.
- `__btrfs_update_delayed_inode()` writes the delayed inode item and optionally deletes the last inode ref/extref.
- `__btrfs_commit_inode_delayed_items()` performs insertions, deletions, records the root in transaction, then updates the inode.

Execution paths:
- `btrfs_run_delayed_items()` flushes all delayed items for transaction commit.
- `btrfs_run_delayed_items_nr()` flushes a bounded number.
- `btrfs_commit_inode_delayed_items()` flushes delayed items for one inode.
- `btrfs_commit_inode_delayed_inode()` commits only the delayed inode item through a joined transaction.
- `btrfs_balance_delayed_items()` schedules background work when delayed item counts cross thresholds.
- `btrfs_async_run_delayed_root()` runs delayed work from the delayed worker queue.

Directory entry APIs:
- `btrfs_insert_delayed_dir_index()` creates a delayed insertion item containing a `btrfs_dir_item` payload.
- `btrfs_delete_delayed_dir_index()` cancels a pending insertion when possible, otherwise queues a deletion.
- `btrfs_inode_delayed_dir_index_count()` exports delayed directory index counter state to the inode.

Readdir and logging:
- `btrfs_readdir_get_delayed_items()` collects delayed insertions/deletions for directory iteration and upgrades inode locking to serialize list use.
- `btrfs_readdir_delayed_dir_index()` emits delayed insertion entries.
- `btrfs_should_delete_dir_index()` filters entries shadowed by delayed deletions.
- `btrfs_log_get_delayed_items()` and `btrfs_log_put_delayed_items()` collect delayed items for directory logging while avoiding duplicate log-list membership.

Inode update helpers:
- `fill_stack_inode_item()` snapshots VFS inode fields into a Btrfs inode item.
- `btrfs_fill_inode()` restores inode fields from a delayed inode item.
- `btrfs_delayed_update_inode()` queues or refreshes a delayed inode item.
- `btrfs_delayed_delete_inode_ref()` queues delayed deletion of a single inode ref, except during log recovery.

Cleanup:
- `btrfs_kill_delayed_inode_items()` kills delayed items for one inode.
- `btrfs_kill_all_delayed_nodes()` kills all nodes for a root.
- `btrfs_destroy_delayed_inodes()` kills all delayed nodes in the filesystem delayed-root list.
- `btrfs_assert_delayed_root_empty()` warns if delayed nodes remain.

Concurrency:
- `delayed_node->mutex` protects rbtrees, delayed inode state, delayed item lists, batch-size counters, and node item count.
- `delayed_root->lock` protects node lists and delayed-root counters.
- Root `delayed_nodes` xarray is protected by `xa_lock()`.
- Delayed item reference counts protect temporary readdir/logging list ownership.

Role in Btrfs:
This file amortizes high-frequency directory and inode metadata changes. It reduces btree churn during creates, deletes, renames, inode updates, logging, and transaction commits while preserving precise metadata reservation accounting.
