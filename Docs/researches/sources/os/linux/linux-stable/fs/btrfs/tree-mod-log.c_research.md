# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.c

## Scope

This file implements Btrfs tree modification logging, which lets readers reconstruct older views of internal B-tree nodes and roots while concurrent tree mutations are happening. It records key pointer changes, moves, block frees, root replacements, and copy operations, then rewinds extent buffers to a requested sequence number.

## Public And Internal APIs Covered

- Sequence-user lifecycle: `btrfs_get_tree_mod_seq()`, `btrfs_put_tree_mod_seq()`, `btrfs_tree_mod_log_lowest_seq()`.
- Log insertion APIs: `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_insert_move()`, `btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_eb_copy()`, `btrfs_tree_mod_log_free_eb()`.
- Rewind/query APIs: `btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`.
- Internal helpers manage RB-tree insertion/search, allocation of `tree_mod_elem`, root ancestry lookup, and reverse replay.

## Control Flow And Behavior

- Active readers register a `btrfs_seq_list` entry and receive a monotonically increasing tree-mod sequence. The first active user sets `BTRFS_FS_TREE_MOD_LOG_USERS`; the last clears it.
- Dropping a sequence user prunes RB-tree log entries whose sequence is older than the lowest remaining active sequence.
- Logging is skipped when there are no users, for leaf extent buffers, and for trees outside the extent tree and filesystem/subvolume trees.
- Log entries are stored in `fs_info->tree_mod_log`, ordered by affected logical address and modification sequence. Root replacement entries are keyed by the new root logical address while carrying the old root address/level/generation.
- Mutation helpers allocate all needed log elements before taking the write lock, then recheck whether logging is still needed. Allocation failures are ignored if logging became unnecessary, but returned if a log user still exists.
- Key removals, replacements, additions, moves, extent-buffer frees, root swaps, and copy operations are represented as `BTRFS_MOD_LOG_*` operations.
- `tree_mod_log_rewind()` walks log entries from newest toward the target sequence and applies inverse operations to a cloned or dummy extent buffer.
- `btrfs_tree_mod_log_rewind()` returns the original read-locked buffer if no rewind is needed; otherwise it releases/frees the input and returns a newly read-locked rewind buffer.
- `btrfs_get_old_root()` finds the oldest logged predecessor of a root at a sequence, reads/clones/allocates the needed root buffer, restores header metadata for old roots, and replays logged changes.

## State And Data Structures

- `struct tree_mod_elem` stores RB linkage, logical address, sequence, operation type, slot/generation, and operation-specific payload.
- Payloads include old key/block pointer data, move destination/count, or old-root logical address and level.
- `fs_info->tree_mod_log_lock` protects both the active sequence list and the modification RB tree.
- Extent-buffer metadata accessors are used to save and restore node keys, block pointers, pointer generations, item counts, owners, levels, bytenrs, and backref revisions.

## Dependencies

- Btrfs core structures: `btrfs_fs_info`, `btrfs_root`, `extent_buffer`, tree roots, and filesystem flags.
- Tree accessors and buffer helpers from Btrfs accessors/disk-io/tree-checking code.
- Linux RB tree, list, atomic64 sequence counter, rwlock, and allocation APIs.

## Risks And Invariants

- Callers rely on exact sequence ordering; pruning too aggressively would break backref and extent iteration over old tree views.
- Only internal nodes are logged. Leaf rewind is intentionally skipped.
- The two-step `tree_mod_need_log()` / `tree_mod_dont_log()` pattern is important because logging may become unnecessary while allocations are being prepared.
- Reverse replay must keep `nritems` and slot movement consistent; invalid move ranges warn and can indicate deeper tree-mod-log corruption.
- Root replacement logging is special because the log is keyed by the new root while old-root reconstruction follows predecessor links.
