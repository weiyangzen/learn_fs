# File Research: sources/os/linux/linux/fs/btrfs/transaction.c

## Purpose

This file implements the Btrfs transaction lifecycle: starting and joining transactions, metadata reservation, root transaction tracking, transaction end, commit orchestration, snapshot creation, qgroup snapshot handling, metadata writeback, superblock persistence, abort cleanup, deleted snapshot cleanup, and transaction handle cache management.

It is one of Btrfs’ central consistency coordination files.

## Transaction State Model

The file documents and implements these states:

- `TRANS_STATE_RUNNING`: normal metadata modifications are allowed.
- `TRANS_STATE_COMMIT_PREP`: a committer has begun preparation.
- `TRANS_STATE_COMMIT_START`: new external starts/attaches are blocked; limited joins may still happen.
- `TRANS_STATE_COMMIT_DOING`: all normal joining is blocked; supporting trees are updated.
- `TRANS_STATE_UNBLOCKED`: tree updates are complete; a new transaction may start while the old one writes out.
- `TRANS_STATE_SUPER_COMMITTED`: superblocks have been written.
- `TRANS_STATE_COMPLETED`: extent commit cleanup is done and the transaction is removed.

`btrfs_blocked_trans_types[]` maps each state to the transaction handle types blocked in that state.

## Public APIs

Transaction lifecycle:
- `btrfs_start_transaction()`
- `btrfs_start_transaction_fallback_global_rsv()`
- `btrfs_join_transaction()`
- `btrfs_join_transaction_spacecache()`
- `btrfs_join_transaction_nostart()`
- `btrfs_attach_transaction()`
- `btrfs_attach_transaction_barrier()`
- `btrfs_end_transaction()`
- `btrfs_end_transaction_throttle()`
- `btrfs_commit_transaction()`
- `btrfs_commit_transaction_async()`
- `btrfs_commit_current_transaction()`
- `btrfs_wait_for_commit()`

Root and cleanup helpers:
- `btrfs_record_root_in_trans()`
- `btrfs_add_dropped_root()`
- `btrfs_add_dead_root()`
- `btrfs_maybe_wake_unfinished_drop()`
- `btrfs_clean_one_deleted_snapshot()`

Writeback and state helpers:
- `btrfs_write_marked_extents()`
- `btrfs_wait_tree_log_extents()`
- `btrfs_transaction_blocked()`
- `btrfs_throttle()`
- `btrfs_should_end_transaction()`
- `btrfs_trans_release_chunk_metadata()`

Abort/cache:
- `__btrfs_abort_transaction()`
- `btrfs_put_transaction()`
- `btrfs_transaction_init()`
- `btrfs_transaction_exit()`

## Starting and Joining Transactions

`join_transaction()`:
- Runs under `fs_info->trans_lock`.
- Rejects work if the filesystem is in error state.
- Joins an existing running transaction if the current state permits the requested type.
- Increments transaction refcount, writer count, and external-writer count.
- Allocates and initializes a new `struct btrfs_transaction` when no transaction exists and the type may start one.
- Initializes delayed-ref xarrays, dirty page/pinned extent trees, wait queues, block group lists, dropped roots, generation, transaction list membership, and state.

`start_transaction()`:
- Reserves qgroup metadata before joining.
- Reserves transaction metadata and delayed-ref bytes.
- Optionally reserves relocation-root space.
- Refills delayed-ref reserve for zero-item throttling starts.
- Allocates a transaction handle from `btrfs_trans_handle_cachep`.
- Handles freeze protection with `sb_start_intwrite()`.
- Waits for blocked transactions when the type permits waiting.
- Joins or starts the transaction.
- Initializes handle fields, local delayed-ref reserve, and writeback inhibition tracking.
- Performs forced chunk allocation when metadata space requires it.
- Records the root in the transaction after `current->journal_info` is initialized.
- Converts qgroup metadata reservation from prealloc to per-transaction.

## Root Tracking

`record_root_in_trans()` and `btrfs_record_root_in_trans()`:
- Track shareable roots modified in a transaction by tagging `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`.
- Update `root->last_trans`.
- Initialize relocation roots when needed.
- Use `BTRFS_ROOT_IN_TRANS_SETUP` plus memory barriers so concurrent users can distinguish in-progress setup from completed recording.

`btrfs_add_dropped_root()`:
- Adds a dropped root to the transaction’s `dropped_roots`.
- Clears the root’s radix transaction tag so commit does not update it.

`switch_commit_roots()`:
- Under `commit_root_sem`, replaces each root’s `commit_root` with the current root node.
- Releases dirty log pages and qgroup swapped-block state.
- Frees roots queued in `dropped_roots`.

## Ending Transactions

`__btrfs_end_transaction()`:
- Handles nested transaction handle references through `use_count`.
- Releases metadata reservations.
- Creates pending block groups.
- Releases chunk metadata reservations.
- Ends freeze write protection for freezable transaction types.
- Uninhibits extent buffer writeback before decrementing writer counters.
- Decrements writer and external-writer counters.
- Wakes commit waiters.
- Releases lockdep maps and transaction references.
- Clears `current->journal_info`.
- Optionally runs delayed iputs.
- Returns abort or read-only errors when applicable.

## Commit Flow

`btrfs_commit_transaction()` is the main transaction commit state machine.

High-level sequence:
1. Stop early if the transaction is already aborted.
2. Release handle metadata reservation.
3. Run an initial delayed-ref flush once per transaction.
4. Create pending block groups.
5. Start dirty block group IO once per transaction.
6. If another committer is active, enqueue pending snapshot, end this handle, and wait.
7. Become the committer by entering `TRANS_STATE_COMMIT_PREP`.
8. Wait for previous transaction completion when required.
9. Enter `TRANS_STATE_COMMIT_START`.
10. Start delalloc flush if `FLUSHONCOMMIT`.
11. Run delayed items.
12. Wait for external writers to drain.
13. Run delayed items again and wait for delalloc.
14. Wait for fast-fsync pending ordered extents.
15. Pause scrub.
16. Enter `TRANS_STATE_COMMIT_DOING`.
17. Wait for all writers to drain.
18. Lock relocation mutex.
19. Create pending snapshots.
20. Run delayed items and delayed refs.
21. Assert delayed root emptiness.
22. Commit filesystem roots and free log root tree.
23. Account qgroup extents.
24. Commit cow-only roots.
25. Add tree and chunk roots to the commit-root switch list.
26. Switch commit roots.
27. Update superblock root pointers and prepare `super_for_commit`.
28. Commit device sizes and clear log error flags.
29. Release chunk metadata.
30. Lock tree log mutex, unblock the transaction, and clear `running_transaction`.
31. Wake waiters and optionally wake cleaner for feature changes.
32. Uninhibit extent buffer writeback.
33. Write and wait dirty transaction extents.
34. Write all superblocks.
35. Mark `TRANS_STATE_SUPER_COMMITTED`.
36. Finish extent commit.
37. Clear full-space flags if needed.
38. Update last committed transaction id.
39. Mark `TRANS_STATE_COMPLETED`.
40. Remove transaction from list, release references, resume scrub, clear journal info, and free the handle.

## Cow-Only and FS Root Commit

`commit_fs_roots()`:
- Iterates radix-tagged roots.
- Clears transaction tags.
- Frees per-transaction qgroup metadata.
- Frees log trees.
- Updates relocation roots.
- Clears `BTRFS_ROOT_FORCE_COW`.
- Updates root item pointers in the tree root.
- Queues roots whose commit root must be switched.

`commit_cowonly_roots()`:
- COWs the tree root node.
- Runs device stats, device replace, qgroups, and space-cache setup.
- Updates all dirty cow-only roots.
- Repeatedly runs delayed refs and writes dirty block groups until stable.
- Updates the committed dev-replace cursor.

`update_cowonly_root()` loops until the root item bytenr/used fields stabilize after updating the root pointer.

## Snapshot Creation

Pending snapshots are created only during transaction commit.

`create_pending_snapshot()`:
- Sets up encrypted filename handling in a NOFS allocation context.
- Allocates a new root objectid.
- Sets qgroup skip id for the new snapshot.
- Runs relocation pre-snapshot hooks and reserves extra metadata if needed.
- Switches transaction block reserve to the pending snapshot reservation.
- Records the parent and source roots in the transaction.
- Allocates a directory index and checks for name conflicts.
- Creates the new qgroup.
- Runs delayed items before root copying.
- Copies the source root item and root block.
- Sets snapshot flags, UUIDs, parent UUID, received UUID handling, and timestamps.
- Inserts the new root item and root refs.
- Opens the new fs root.
- Runs relocation post-snapshot hooks.
- Performs qgroup inheritance/accounting.
- Inserts the directory item and updates parent inode.
- Adds UUID tree entries.
- Restores reserves, clears skip qgroup, frees temporary resources, and stores errors in `pending->error`.

`qgroup_account_snapshot()` performs a special mini-commit for full qgroup accounting so snapshot inheritance sees consistent root and extent usage.

## Writeback and Waiting

`btrfs_write_marked_extents()`:
- Converts dirty extent bits to `EXTENT_NEED_WAIT`.
- Starts writeback for btree inode ranges.
- If marking fails with `-ENOMEM`, it still waits for writeback to avoid committing a superblock that points to unwritten metadata.

`__btrfs_wait_marked_extents()`:
- Waits on ranges marked `EXTENT_NEED_WAIT`.
- Clears that state where possible.

`btrfs_wait_extents()` and `btrfs_wait_tree_log_extents()`:
- Convert btree/log writeback error flags into `-EIO`.

`btrfs_write_and_wait_transaction()`:
- Writes and waits all transaction dirty pages and releases the transaction dirty-page io tree.

## Abort and Cleanup

`cleanup_transaction()`:
- Aborts the transaction.
- If still running, transitions to commit-doing and waits for writers.
- Removes the transaction from the transaction list.
- Calls `btrfs_cleanup_one_transaction()`.
- Clears `running_transaction`.
- Releases freeze protection and transaction refs.
- Cancels scrub unless relocation is running.
- Uninhibits writeback and frees the handle.

`btrfs_cleanup_pending_block_groups()`:
- Releases delayed-ref reservations for pending new block groups on abort.

`__btrfs_abort_transaction()`:
- Stores the abort error in both handle and transaction.
- Dumps space info for first `-ENOSPC` abort.
- Wakes transaction waiters.
- Marks the filesystem error state.

## Research Notes

This file is the transaction consistency spine for Btrfs. The most sensitive areas are the transition between `COMMIT_DOING` and `UNBLOCKED`, snapshot creation during commit, qgroup mini-commit behavior, writer/extwriter draining, and the ordering of metadata writeback versus superblock writes.
