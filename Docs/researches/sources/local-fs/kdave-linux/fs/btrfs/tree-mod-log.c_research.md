# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.c

## Purpose

`tree-mod-log.c` implements Btrfs' tree modification log: a sequence-numbered, reversible log of B-tree node/root changes used to reconstruct older views of metadata trees while concurrent modification is happening.

Its main consumer is backreference and extent-walking logic that needs a consistent historical view of extent and filesystem trees. Rather than freezing all tree updates, callers register a tree-mod-log sequence blocker, mutations record reversible operations, and later readers rewind extent buffers or root nodes to the state visible at that sequence.

## Main Data Structures

`struct tree_mod_elem` is the private log record stored in `fs_info->tree_mod_log`, an rb-tree ordered by affected logical address and sequence number. It records:

- `logical`: affected tree block logical address, or the new root address for root replacement entries.
- `seq`: global tree modification sequence.
- `op`: one of `BTRFS_MOD_LOG_*`.
- `slot` and `generation`: affected node slot metadata.
- `slot_change`: saved key/blockptr for add/remove/replace reversal.
- `move`: source/destination/count metadata for key moves.
- `old_root`: old logical address and level for root replacement.

`struct tree_mod_root` stores old root identity for `BTRFS_MOD_LOG_ROOT_REPLACE`.

The global state is carried in `struct btrfs_fs_info`: `tree_mod_seq`, `tree_mod_seq_list`, `tree_mod_log`, `tree_mod_log_lock`, and the `BTRFS_FS_TREE_MOD_LOG_USERS` flag.

## Sequence Lifecycle

`btrfs_get_tree_mod_seq()` registers a `struct btrfs_seq_list` blocker if it does not already have a sequence, appends it to `fs_info->tree_mod_seq_list`, sets `BTRFS_FS_TREE_MOD_LOG_USERS`, and returns the blocker sequence.

`btrfs_put_tree_mod_seq()` removes a blocker and prunes log records older than the lowest remaining blocker sequence. If the removed blocker was not the oldest active blocker, pruning is skipped because earlier readers may still need older log entries. When the blocker list becomes empty, `BTRFS_FS_TREE_MOD_LOG_USERS` is cleared.

This means tree-mod-log retention is driven by the oldest active reader, not by transaction boundaries.

## Logging Gate

`tree_mod_need_log()` cheaply checks whether logging might be needed. It rejects logging when there are no users or when the extent buffer belongs to a tree that does not need historical backref consistency.

`tree_mod_dont_log()` is the locking version. It takes `tree_mod_log_lock` for writing only if users exist and the affected buffer should be logged. Callers allocate records before this point, then re-check under the lock to avoid racing with the last blocker going away. If logging is no longer needed, allocation failures are ignored.

`skip_eb_logging()` excludes leaves and non-target trees. The file logs internal nodes from the extent tree and filesystem trees, because those are the trees needed for consistent extent/backref iteration.

## Log Insertion Paths

`tree_mod_log_insert()` assigns a fresh sequence and inserts the record into the rb-tree. For equal logical addresses, larger sequence numbers are placed toward the left side, matching the search logic used for newest/oldest lookup.

Public insertion helpers cover B-tree edit patterns:

- `btrfs_tree_mod_log_insert_key()` logs single key add/remove/replace-style operations.
- `btrfs_tree_mod_log_insert_move()` logs a contiguous key move and also logs overwritten destination slots when moving toward lower slots.
- `btrfs_tree_mod_log_eb_copy()` logs key copies between nodes, destination-side moves, source removals, and source-side compaction moves.
- `btrfs_tree_mod_log_free_eb()` logs all keys in a node as removed while freeing.
- `btrfs_tree_mod_log_insert_root()` logs root replacement and optionally logs removal of old-root keys.

Most insertion helpers allocate all needed records first, acquire the tree-mod-log write lock, insert records in a sequence that can later be rewound, and unwind any already-inserted records on failure.

## Search And Rewind

`tree_mod_log_search()` returns the newest log entry for a logical address at or newer than a minimum sequence. `tree_mod_log_search_oldest()` returns the oldest such entry. Both use `__tree_mod_log_search()` under `tree_mod_log_lock`.

`tree_mod_log_oldest_root()` follows `BTRFS_MOD_LOG_ROOT_REPLACE` links backward from the current root to find the oldest predecessor relevant to a sequence. Root replacement records are keyed by the new root address, so this helper walks from current root to old roots until it finds the earliest required root state.

`tree_mod_log_rewind()` applies inverse operations to an extent buffer while traversing log records in sequence order for the same logical address:

- Removed keys are restored with saved key/blockptr/generation.
- Replaced keys are restored.
- Added keys reduce item count because the inverse is removal.
- Move operations are reversed with `memmove_extent_buffer()`.
- Root replacement is ignored for non-root node rewind; root replacement is handled before choosing the buffer.

It tracks `max_slot` separately from item count to sanity-check move ranges during partial rewind states.

## Public Historical View APIs

`btrfs_tree_mod_log_rewind()` rewinds a locked extent buffer to a given sequence. If the buffer needs rewind, it clones the buffer or creates a dummy buffer for a node that was freed, releases the original, locks the replacement, replays inverse operations, and returns the rewound buffer locked.

`btrfs_get_old_root()` returns a locked extent buffer representing a root node as of `time_seq`. It may return the current root node, clone the current root, read and clone an old root from disk, or create a dummy extent buffer for a freed old root. It includes a race check after reading an old root because new tree-mod-log operations can be inserted between lookup and cloning.

`btrfs_old_root_level()` reports the historical level of a root at a sequence by checking the oldest root replacement record.

`btrfs_tree_mod_log_lowest_seq()` returns the oldest active blocker sequence or `0` if no users exist.

## Dependencies

This file depends on Btrfs core metadata helpers from `accessors.h`, tree buffer allocation/cloning/locking from `disk-io.h`, filesystem state from `fs.h`, diagnostics from `messages.h`, and structural checks from `tree-checker.h`.

It is tightly coupled to Btrfs internal node layout through helpers such as `btrfs_node_key()`, `btrfs_set_node_key()`, `btrfs_node_blockptr()`, `btrfs_set_node_blockptr()`, `btrfs_header_level()`, and `btrfs_header_nritems()`.

## Invariants And Risks

The core invariant is that every logged mutation must contain enough old state to reverse it and must be inserted in an order that matches rewind expectations. Bugs here can corrupt reconstructed metadata views, causing incorrect backref walks, false leak reports, missed references, or kernel assertions.

High-risk areas include move logging, `eb_copy()` multi-record rollback, dummy buffer creation for freed nodes, root replacement chains, and races between log search and reading old roots. The code relies on careful lock ordering: records are inserted under `tree_mod_log_lock`, extent buffers are cloned/read-locked separately, and readers replay records under the tree-mod-log read lock.
