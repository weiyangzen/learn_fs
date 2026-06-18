# File Research: sources/local-fs/btrfs-linux/fs/btrfs/transaction.c

## Summary
Implements Btrfs transaction lifecycle management: joining/starting transactions, reserving metadata, committing roots and superblocks, creating pending snapshots, waiting for commits, handling aborts, and cleaning up committed or failed transactions.

## Main Responsibilities
- Maintain transaction state transitions from running through commit prep/start/doing/unblocked/super committed/completed.
- Allocate, join, reference, and release `btrfs_transaction` and `btrfs_trans_handle`.
- Reserve and release transaction metadata, qgroup metadata, delayed-ref metadata, chunk metadata, and relocation-root metadata.
- Record dirty roots in a transaction and switch commit roots after commit.
- Commit fs roots, cow-only roots, dirty block groups, delayed refs/items, qgroups, device stats, dev-replace state, and superblocks.
- Create pending snapshots at commit time with qgroup inheritance, root refs, dir items, UUID-tree entries, and relocation hooks.
- Provide synchronous/asynchronous commit helpers and wait-for-commit barriers.
- Abort transactions and clean up aborted transaction state.

## Key APIs
- Start/join/attach: `btrfs_start_transaction()`, `btrfs_start_transaction_fallback_global_rsv()`, `btrfs_join_transaction()`, `btrfs_join_transaction_spacecache()`, `btrfs_join_transaction_nostart()`, `btrfs_attach_transaction()`, `btrfs_attach_transaction_barrier()`.
- End/commit/wait: `btrfs_end_transaction()`, `btrfs_end_transaction_throttle()`, `btrfs_commit_transaction()`, `btrfs_commit_transaction_async()`, `btrfs_commit_current_transaction()`, `btrfs_wait_for_commit()`, `btrfs_throttle()`.
- Root tracking: `btrfs_record_root_in_trans()`, `btrfs_add_dropped_root()`, `btrfs_add_dead_root()`, `btrfs_maybe_wake_unfinished_drop()`, `btrfs_clean_one_deleted_snapshot()`.
- I/O waiting: `btrfs_write_marked_extents()`, `btrfs_wait_tree_log_extents()`.
- Abort/init: `__btrfs_abort_transaction()`, `btrfs_transaction_init()`, `btrfs_transaction_exit()`.

## Important Behavior
`join_transaction()` either attaches to an existing running transaction or creates a new one, honoring the blocked transaction type table for each commit state. Transaction creation initializes delayed-ref xarrays, dirty/pinned extent I/O trees, block-group lists, snapshot/drop lists, wait queues, refcounts, and bumps `fs_info->generation`.

`start_transaction()` reserves qgroup metadata, btree metadata, delayed-ref space, and optional relocation-root space before joining. It handles nested transaction handles through `current->journal_info`, freeze protection for freezable transaction types, blocked-current-transaction waits, delayed-ref reserve refills, forced chunk allocation, and root recording after handle setup.

`btrfs_commit_transaction()` is the central commit sequence. It runs delayed refs/items, starts dirty block-group I/O, serializes against other committers, waits for previous transactions as needed, blocks external writers, waits pending ordered extents, pauses scrub, creates snapshots, commits fs roots and cow-only roots, switches commit roots, updates the super copy, unblocks new transactions before writing metadata/superblocks, writes and waits dirty btree extents, writes all supers, finishes extent commit, marks the transaction completed, and releases references.

Snapshot creation is deliberately delayed into commit. `create_pending_snapshot()` allocates a new root id, sets qgroup skip state, handles relocation reservation/hooks, records parent/source roots, copies the source root, inserts root items and root refs, gets the new fs root, performs qgroup full/simple inheritance, inserts the parent dir item, updates parent inode, and records UUID-tree entries.

Abort cleanup marks the transaction aborted, forces the filesystem read-only through fs error handling, wakes waiters, cancels scrub unless relocation is running, cleans one transaction, drops pending block groups, releases reservations, and removes the failed transaction from lists.

## State and Synchronization
Transaction state is protected mainly by `fs_info->trans_lock`; writer counts use atomics and wait queues. Commit-root switching uses `commit_root_sem`. Root transaction setup uses `reloc_mutex` plus `BTRFS_ROOT_IN_TRANS_SETUP` memory barriers. Commit critical sections coordinate with scrub, relocation, tree-log mutex, block-group mutexes, freeze intwrite references, and lockdep maps for transaction states/writer counts.

## Risks
Commit ordering is fragile: delayed refs, qgroups, snapshots, root updates, dirty block groups, metadata writeback, and superblock writes must occur in the right sequence. Error paths must release reservations without letting another task observe partially committed state. Snapshot qgroup accounting contains explicit race-window comments and a simplified internal commit, making it particularly sensitive to changes.
