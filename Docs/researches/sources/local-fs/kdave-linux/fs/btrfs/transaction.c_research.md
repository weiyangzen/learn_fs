# File Research: sources/local-fs/kdave-linux/fs/btrfs/transaction.c

## Purpose

This file implements the Btrfs transaction lifecycle: starting/joining transactions, metadata reservation, root tracking, transaction end, commit orchestration, snapshot creation during commit, writeback/superblock persistence, abort cleanup, deleted snapshot cleanup, and transaction handle cache initialization.

It is one of the central coordination files for Btrfs metadata consistency.

## Transaction State Model

The file documents and implements a staged transaction state machine:

- `TRANS_STATE_RUNNING`: normal metadata modifications allowed.
- `TRANS_STATE_COMMIT_PREP`: a committer has started preparing.
- `TRANS_STATE_COMMIT_START`: new external starts/attaches are blocked; joins may still be allowed depending on type.
- `TRANS_STATE_COMMIT_DOING`: all normal joining is blocked; supporting trees are updated.
- `TRANS_STATE_UNBLOCKED`: tree updates are complete; a new transaction may start while old one writes out.
- `TRANS_STATE_SUPER_COMMITTED`: superblock has been written.
- `TRANS_STATE_COMPLETED`: extent commit cleanup done and transaction removed.

`btrfs_blocked_trans_types[]` defines which transaction handle types are blocked in each state.

## Major Public APIs

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

Root/snapshot helpers:
- `btrfs_record_root_in_trans()`
- `btrfs_add_dropped_root()`
- `btrfs_add_dead_root()`
- `btrfs_maybe_wake_unfinished_drop()`
- `btrfs_clean_one_deleted_snapshot()`

Writeback/helpers:
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

## Transaction Creation and Joining

`join_transaction()`:
- Runs under `fs_info->trans_lock`.
- Rejects new work on filesystem error.
- Joins existing running transactions if the transaction state allows the requested type.
- Increments writer/extwriter counters and transaction refcount.
- Allocates and initializes a new `struct btrfs_transaction` when no transaction exists and the type permits starting one.
- Initializes delayed-ref xarrays, dirty page trees, pinned extent tree, block group lists, dropped roots, wait queues, generation, and transaction list membership.

`start_transaction()`:
- Handles qgroup metadata preallocation.
- Reserves transaction metadata and delayed-ref space.
- Optionally reserves extra space for relocation root creation.
- Refills delayed-ref reserve for zero-item throttling starts.
- Allocates a transaction handle from `btrfs_trans_handle_cachep`.
- Handles freeze protection with `sb_start_intwrite()`.
- Waits for blocked transactions when appropriate.
- Joins/starts the transaction.
- Sets up transaction handle fields and local delayed-ref reserve.
- Performs forced chunk allocation when metadata space requires it.
- Records the root in the transaction after `current->journal_info` is initialized to avoid recursion deadlocks.
- Converts qgroup prealloc reservation to per-transaction reservation.

## Root Tracking

`record_root_in_trans()` and `btrfs_record_root_in_trans()`:
- Ensure shareable roots modified in a transaction are tagged in `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`.
- Update `root->last_trans`.
- Initialize relocation roots when needed.
- Use `BTRFS_ROOT_IN_TRANS_SETUP` and memory barriers so concurrent users can distinguish setup from completed root transaction recording.

`btrfs_add_dropped_root()`:
- Adds a dropped root to the transaction’s `dropped_roots`.
- Clears the root’s radix transaction tag so commit does not update it.

`switch_commit_roots()`:
- Under `commit_root_sem`, replaces each root’s `commit_root` with the current root node.
- Releases dirty log pages and qgroup swapped-block state.
- Frees roots listed in `dropped_roots`.

## Ending Transactions

`__btrfs_end_transaction()`:
- Handles nested handle references through `use_count`.
- Releases metadata reservations.
- Creates pending block groups.
- Releases chunk metadata reservations.
- Ends freeze write protection for freezable transaction types.
- Uninhibits extent buffer writeback before decrementing writer counters.
- Decrements transaction writer/extwriter counters.
- Wakes commit waiters.
- Releases lockdep maps and transaction references.
- Clears `current->journal_info`.
- Optionally runs delayed iputs.
- Returns abort or read-only errors when applicable.

## Commit Flow

`btrfs_commit_transaction()` is the main commit state machine.

High-level sequence:
1. Validate handle use count and acquire commit-prep lockdep state.
2. Stop early on already aborted transaction.
3. Release handle metadata reservation.
4. Run an initial delayed-ref flush once per transaction.
5. Create pending block groups.
6. Start dirty block group I/O once per transaction.
7. If another committer is already active, enqueue pending snapshot, end this handle, and wait for target commit state.
8. Become the committer by moving to `TRANS_STATE_COMMIT_PREP`.
9. Wait for previous transaction if needed.
10. Move to `TRANS_STATE_COMMIT_START`.
11. Start delalloc flush if `FLUSHONCOMMIT`.
12. Run delayed items.
13. Wait for external writers to drain.
14. Run delayed items again and wait delalloc.
15. Wait for fast-fsync pending ordered extents.
16. Pause scrub.
17. Move to `TRANS_STATE_COMMIT_DOING`.
18. Wait for all writers to drain.
19. Lock relocation mutex.
20. Create pending snapshots.
21. Run delayed items and delayed refs.
22. Assert delayed root empty.
23. Commit filesystem roots and free log root tree.
24. Account qgroup extents.
25. Commit cow-only roots.
26. Add tree/chunk roots to switch list and switch commit roots.
27. Update super root pointers and prepare `super_for_commit`.
28. Commit device sizes and clear log error flags.
29. Release chunk metadata.
30. Lock tree log mutex, unblock transaction, and set `running_transaction = NULL`.
31. Wake waiters and optionally wake cleaner for feature changes.
32. Uninhibit extent buffer writeback.
33. Write and wait dirty transaction extents.
34. Write all superblocks.
35. Mark `TRANS_STATE_SUPER_COMMITTED`.
36. Finish extent commit.
37. Clear full-space flags if needed.
38. Update last committed transaction id.
39. Mark `TRANS_STATE_COMPLETED`.
40. Remove from transaction list, release references, resume scrub, clear journal info, and free handle.

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
- Updates committed dev-replace cursor.

`update_cowonly_root()` loops until the root item bytenr/used fields stabilize after updating the root pointer.

## Snapshot Creation

Pending snapshots are created only during transaction commit.

`create_pending_snapshot()`:
- Sets up encrypted filename with NOFS allocation context.
- Allocates a new root objectid.
- Sets qgroup skip id for the new snapshot.
- Runs relocation pre-snapshot hooks and reserves extra metadata if needed.
- Switches transaction block reserve to the pending snapshot reservation.
- Records the parent root and source root in the transaction.
- Allocates a directory index and verifies name absence.
- Creates the new qgroup.
- Runs delayed items before copying the root.
- Copies source root item and root block.
- Sets snapshot flags, UUIDs, parent UUID, received UUID handling, and timestamps.
- Inserts the new root item and root refs.
- Opens the new fs root.
- Runs relocation post-snapshot hook.
- Performs qgroup inheritance/accounting.
- Inserts the directory item and updates parent inode.
- Adds UUID tree entries.
- Restores reserves, clears skip qgroup, frees name/root item resources, and stores errors in `pending->error`.

`qgroup_account_snapshot()` performs a special mini-commit sequence for full qgroup accounting so snapshot qgroup inheritance sees consistent root and extent accounting.

## Writeback and Waiting

`btrfs_write_marked_extents()`:
- Converts dirty extent bits to `EXTENT_NEED_WAIT`.
- Starts writeback for btree inode ranges.
- If marking fails with `-ENOMEM`, still waits for writeback to avoid committing unwritten metadata.

`__btrfs_wait_marked_extents()` waits on ranges marked `EXTENT_NEED_WAIT` and clears that state.

`btrfs_wait_extents()` and `btrfs_wait_tree_log_extents()` translate writeback error flags into `-EIO`.

`btrfs_write_and_wait_transaction()` writes and waits all transaction dirty pages and releases the transaction dirty-page io tree.

## Abort and Cleanup

`cleanup_transaction()`:
- Calls `btrfs_abort_transaction()`.
- If still running, transitions to commit-doing and waits for writers.
- Removes the transaction from the transaction list.
- Calls `btrfs_cleanup_one_transaction()`.
- Clears `running_transaction`.
- Releases freeze protection and transaction refs.
- Cancels scrub unless relocation is running.
- Uninhibits writeback and frees handle.

`btrfs_cleanup_pending_block_groups()` releases delayed-ref reservations for pending new block groups on abort.

`__btrfs_abort_transaction()`:
- Stores abort error in both handle and transaction.
- Dumps space info for first `-ENOSPC` abort.
- Wakes transaction waiters.
- Delegates filesystem error handling to `__btrfs_handle_fs_error()`.

## Deleted Snapshot Cleanup

`btrfs_add_dead_root()` adds roots to `fs_info->dead_roots`, prioritizing unfinished drops.

`btrfs_clean_one_deleted_snapshot()`:
- Removes one root from `dead_roots`.
- Kills delayed nodes.
- Calls `btrfs_drop_snapshot()` with mixed-backref behavior based on root header.
- Drops the root reference.
- Returns `1` when more work may remain, `0` when none or on error.

## Important Concurrency and Consistency Points

- `fs_info->trans_lock` protects running transaction pointer, transaction state transitions, and transaction list manipulations.
- Writer counters gate commit phases and prevent metadata mutation while roots/supers are being committed.
- Extwriter counters allow commit to block userspace/external transaction starts before fully blocking all writers.
- `tree_log_mutex` prevents a log tree superblock write from racing between transaction unblock and transaction superblock write.
- `reloc_mutex` prevents relocation from changing extent layout during critical commit phases.
- `commit_root_sem` protects commit root switching.
- Scrub is paused during the critical commit section.
- Lockdep state annotations model transaction waiting and state transitions.

## Research Notes

This file is the authoritative Btrfs transaction coordinator. Its behavior depends on many subsystems: delayed refs/items, qgroups, block groups, chunk allocation, relocation, tree log, scrub, dev-replace, dirty block group writeback, root tree updates, and superblock writes. Most subtle bugs here would be ordering bugs: allowing a writer too late, publishing a superblock before metadata writeback, losing qgroup/snapshot consistency, or mishandling abort cleanup while other tasks still hold transaction references.
