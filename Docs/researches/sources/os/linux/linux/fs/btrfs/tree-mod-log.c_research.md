# File Research: sources/os/linux/linux/fs/btrfs/tree-mod-log.c

## Purpose

`tree-mod-log.c` implements Btrfs' tree modification log. The log gives long-running readers, especially backref and extent walkers, a stable historical view of internal tree nodes while concurrent operations split, move, replace, free, or promote tree blocks.

The implementation records reversible modifications to non-leaf extent buffers from the extent tree and filesystem trees. A caller obtains a sequence number before walking, writers append tree modification records while that sequence is active, and readers can rewind cloned extent buffers or root nodes back to the requested sequence.

## Core Data Model

`struct tree_mod_elem` is the private log record. It is keyed in an rb-tree by affected logical address and sequence number. Each record stores an operation code, slot, generation, and operation-specific payload:

- key slot changes keep the old key, block pointer, and generation.
- move records keep destination slot and item count.
- root replacement records keep the old root logical address and level.

`struct tree_mod_root` is a compact payload for root replacement history. The public `struct btrfs_seq_list` lives in the header and represents one active log user.

## Sequence Users and Garbage Collection

`btrfs_get_tree_mod_seq()` assigns a fresh sequence to a user that does not already have one, appends it to `fs_info->tree_mod_seq_list`, and sets `BTRFS_FS_TREE_MOD_LOG_USERS`.

`btrfs_put_tree_mod_seq()` removes a user and frees obsolete log records. If lower-sequence users remain, no cleanup is possible. Otherwise all log records with `tm->seq < min_seq` are removed from `fs_info->tree_mod_log`. If the last user leaves, the users flag is cleared and the cleanup threshold becomes `BTRFS_SEQ_LAST`.

`btrfs_tree_mod_log_lowest_seq()` exposes the oldest active sequence, returning 0 when there are no users.

## Logging Filters

`skip_eb_logging()` avoids logging leaves and trees that are irrelevant to the backref use case. Internal nodes from the extent tree and subvolume trees are logged; other trees are skipped.

`tree_mod_need_log()` is the cheap unlocked predicate used before allocation. `tree_mod_dont_log()` rechecks under `tree_mod_log_lock`; when it returns false, it leaves the write lock held so the caller can insert all records atomically relative to sequence users.

This two-step pattern avoids unnecessary allocations when no historical readers exist, while still handling races where readers appear or disappear between the first check and insertion.

## Log Insertion

`tree_mod_log_insert()` assigns a new sequence and inserts a record into the rb-tree. The tree's ordering is intentionally unusual: lower logical addresses go down the left branch, and for the same logical address lower sequence numbers also go left. The paired search helpers understand this order and find either the oldest or newest relevant record for a block.

Allocation helpers prepare records from current node slots before the live tree is modified:

- `alloc_tree_mod_elem()` captures a key pointer slot.
- `tree_mod_log_alloc_move()` captures a move operation.
- `tree_mod_log_free_eb()` inserts a whole set of removal records in reverse slot order.

## Recorded Tree Operations

`btrfs_tree_mod_log_insert_key()` logs a single key add, remove, replace, or related slot operation.

`btrfs_tree_mod_log_insert_move()` logs key movement within a node. When a move toward lower slots overwrites entries, it first logs the overwritten keys as `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_MOVING`, then logs the move itself.

`btrfs_tree_mod_log_insert_root()` logs root replacement, optionally logging all removed children from the old root when the old root is being freed.

`btrfs_tree_mod_log_eb_copy()` logs a copy between internal extent buffers. It records destination-side movement, source removals, destination additions, and source-side movement in the order needed to reconstruct the previous state.

`btrfs_tree_mod_log_free_eb()` logs removal of every key pointer in an internal extent buffer that is being freed.

All multi-record paths allocate first, acquire `tree_mod_log_lock`, then either insert the complete group or unwind partial inserts on failure.

## Searching and Rewinding

`tree_mod_log_search_oldest()` returns the oldest log record for a block at or after a sequence. `tree_mod_log_search()` returns the newest such record. Both are built on `__tree_mod_log_search()`.

`tree_mod_log_oldest_root()` follows `BTRFS_MOD_LOG_ROOT_REPLACE` records backwards from the current root logical address to find the old root that corresponds to a historical sequence.

`tree_mod_log_rewind()` applies inverse operations from newest to oldest for one logical block until it reaches entries older than the requested sequence. It restores removed keys, undoes replacements, drops added keys, reverses moves with `memmove_extent_buffer()`, and ignores root replacement records for non-root rewinds. It also tracks a conservative `max_slot` to warn about invalid move ranges.

## Public Historical Views

`btrfs_tree_mod_log_rewind()` rewinds a read-locked extent buffer. If no matching record exists, or if the buffer is a leaf, it returns the original buffer. Otherwise it clones the buffer or allocates a dummy buffer for a block that had been freed, unlocks/releases the input buffer, locks the replacement, replays inverse log operations, and returns the rewound buffer.

`btrfs_get_old_root()` returns a read-locked root node as of a sequence. It handles root replacement specially: it may read the old root from disk, allocate a dummy buffer, or clone the current root, then replay relevant log entries. It rechecks the newest matching log entry after cloning a disk-read old root to avoid replaying a log sequence inconsistent with the cloned buffer's item count.

`btrfs_old_root_level()` is a lightweight helper that reports the historical root level for a sequence.

## Concurrency and Failure Behavior

The log uses `fs_info->tree_mod_log_lock` for both the rb-tree and sequence-user list. Writers hold it while inserting complete operation groups. Search and rewind hold the read side while walking log records.

Memory allocation is done before taking the write lock where possible. If allocation failed but the locked recheck shows logging is unnecessary, the function returns success. If logging is necessary, allocation failures propagate as `-ENOMEM`.

The code uses `BUG_ON`, `ASSERT`, and `WARN_ON` for invariants that indicate corrupt or inconsistent replay state, such as invalid slot counts or impossible sequence ordering.

## Filesystem Role

This file is a core consistency aid for Btrfs' copy-on-write metadata. It does not persist data on disk; it records transient in-memory history only while users hold tree mod sequences. Its correctness is essential for backref walking, delayed reference processing, send/relocation style tree reads, and other code that needs a coherent old view of metadata while writers continue modifying live trees.
