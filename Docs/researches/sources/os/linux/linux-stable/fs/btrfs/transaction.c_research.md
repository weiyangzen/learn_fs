# File Research: sources/os/linux/linux-stable/fs/btrfs/transaction.c

## Role

Core Btrfs transaction lifecycle implementation. This file manages transaction creation/joining, metadata/qgroup reservations, root recording, delayed refs/items, commit sequencing, pending snapshots, superblock updates, transaction abort cleanup, and wait/wakeup coordination.

## Transaction State Machine

The file documents and implements transitions through:

- `TRANS_STATE_RUNNING`
- `TRANS_STATE_COMMIT_PREP`
- `TRANS_STATE_COMMIT_START`
- `TRANS_STATE_COMMIT_DOING`
- `TRANS_STATE_UNBLOCKED`
- `TRANS_STATE_SUPER_COMMITTED`
- `TRANS_STATE_COMPLETED`

`btrfs_blocked_trans_types[]` defines which start/join modes are blocked at each state.

## Start and Join Path

- `join_transaction()`: attaches to an existing running transaction or allocates a new `btrfs_transaction`. It initializes delayed refs, dirty page trees, pinned extents, pending snapshot/device/block-group lists, counters, wait queues, transid/generation, and tree-mod-log boundaries.
- `start_transaction()`: high-level transaction handle setup. It reserves qgroup metadata, transaction metadata, delayed-ref metadata, optional relocation-root space, handles freezer write refs, waits for blocked commits, joins/creates the transaction, initializes the handle, optionally triggers chunk allocation, records the root, and converts qgroup reservation from prealloc to per-transaction.
- Public wrappers include `btrfs_start_transaction()`, fallback-global-reserve start, join, spacecache join, nostart join, attach, and attach-barrier variants.

## Root Recording

- `record_root_in_trans()`: tags shareable roots in `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`, updates `last_trans`, and initializes relocation roots under setup barriers.
- `btrfs_record_root_in_trans()`: public wrapper using `reloc_mutex` to serialize first setup.
- `btrfs_add_dropped_root()`: moves roots to transaction dropped list and clears their transaction radix tag.

## Ending and Waiting

- `btrfs_end_transaction()` / `btrfs_end_transaction_throttle()`: release metadata reservations, create pending block groups, release chunk metadata, drop freezer refs, uninhibit extent-buffer writeback, decrement writer counters, wake commit waiters, and free the handle.
- `btrfs_wait_for_commit()`: waits for a specific transid or latest committing transaction.
- `wait_for_commit()`: waits for at least `SUPER_COMMITTED` or `COMPLETED`, with ordering across earlier transactions.
- `btrfs_should_end_transaction()` and `btrfs_throttle()` expose pressure/blocked-commit checks to callers.

## Commit Writeout

- `btrfs_write_marked_extents()`: starts writeback for dirty btree ranges and marks ranges needing wait.
- `__btrfs_wait_marked_extents()` / `btrfs_wait_extents()`: wait for btree writeback and convert fs error flags to `-EIO`.
- `btrfs_write_and_wait_transaction()`: writes and waits for transaction dirty btree pages, then releases the dirty-pages io tree.
- `btrfs_wait_tree_log_extents()`: log-tree equivalent with log error flags.

## Root Commit Work

- `commit_fs_roots()`: processes radix-tagged fs roots, frees log trees, updates relocation roots, clears forced COW, switches dirty roots, and updates root items in the tree root.
- `commit_cowonly_roots()`: updates chunk/tree/cow-only roots, runs device stats, dev-replace, qgroups, space cache, delayed refs, and dirty block group writeout until stable.
- `switch_commit_roots()`: swaps each dirty root’s `commit_root` to current root node, cleans qgroup swapped blocks, and drops freed roots.

## Snapshot Commit Path

- `create_pending_snapshot()`: creates scheduled snapshots during commit. It handles fscrypt name setup, new objectid allocation, qgroup skip setup, relocation pre/post hooks, parent dir index checks, qgroup creation, delayed items, root copy, root item/guid/timestamp setup, root refs, new fs root lookup, qgroup inheritance/accounting, dir item insertion, parent inode update, and UUID tree updates.
- `qgroup_account_snapshot()`: special full-qgroup path that records source/parent roots, flushes delayed refs, commits fs roots, accounts extents, inherits qgroups, performs a simplified cow-only commit/writeout, switches commit roots, and forces parent root recording.
- `create_pending_snapshots()`: drains the transaction pending snapshot list.

## Main Commit Sequence

`btrfs_commit_transaction()`:

1. Releases handle metadata reservation and runs an initial delayed-ref flush.
2. Creates pending block groups and starts dirty block group writeout once.
3. Moves transaction to `COMMIT_PREP`/`COMMIT_START`, waits for earlier commits if needed.
4. Starts optional delalloc flush, runs delayed items, waits for external writers, ordered extents, and all other transaction writers.
5. Pauses scrub, moves to `COMMIT_DOING`, adds pending snapshot, and enters the critical commit section.
6. Creates snapshots, flushes delayed items and refs, commits fs roots, frees log root tree, accounts qgroups, commits cow-only roots, switches commit roots, updates super roots and device sizes.
7. Sets transaction `UNBLOCKED`, clears `running_transaction`, wakes new transaction starters, writes btree blocks, writes supers, marks `SUPER_COMMITTED`.
8. Finishes extent commit, clears free-space fullness if needed, records last committed transid, marks `COMPLETED`, removes transaction from list, releases references, resumes scrub, and frees the handle.

## Abort and Cleanup

- `cleanup_transaction()`: aborts, waits for writers, removes the transaction from lists, runs transaction cleanup, clears `running_transaction`, drops freezer refs, cancels scrub unless relocation is running, uninhibits writeback, and frees the handle.
- `btrfs_cleanup_pending_block_groups()`: releases delayed-ref reservations for new block groups on abort.
- `__btrfs_abort_transaction()`: records abort on handle and transaction, optionally dumps ENOSPC space info, wakes waiters, and marks filesystem error state.
- `btrfs_clean_one_deleted_snapshot()`: cleaner helper for dead snapshot roots.

## Concurrency and Locking

- `fs_info->trans_lock` protects `running_transaction`, transaction list membership, state changes, and transaction waits.
- Atomic writer/extwriter counters gate commit progression.
- `reloc_mutex` prevents relocation racing with root/snapshot commit work.
- `tree_log_mutex` prevents log tree superblock commits from racing the main superblock commit.
- `commit_root_sem` protects commit-root switching.
- Scrub is paused across the critical commit region.
