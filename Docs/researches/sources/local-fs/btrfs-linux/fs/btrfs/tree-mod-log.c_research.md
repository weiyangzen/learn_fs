# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.c

Implements the Btrfs tree modification log, a sequence-numbered reverse-operation log used to reconstruct older views of internal tree nodes and roots while backref/extents code is walking metadata concurrently with tree updates.

Key entry points:
- `btrfs_get_tree_mod_seq()` registers a tree-mod-log user, assigns a blocker sequence, and enables `BTRFS_FS_TREE_MOD_LOG_USERS`.
- `btrfs_put_tree_mod_seq()` unregisters a user and garbage-collects log entries older than the lowest remaining blocker sequence.
- `btrfs_tree_mod_log_insert_key()` records key pointer add/remove/replace operations for an internal extent buffer slot.
- `btrfs_tree_mod_log_insert_move()` records an internal node key-range move and any overwritten keys that must be restored when rewinding.
- `btrfs_tree_mod_log_insert_root()` records root replacement and, optionally, removal of the old root's internal-node keys while freeing.
- `btrfs_tree_mod_log_eb_copy()` logs key pointer transfers between internal nodes, including source/destination shifts around the copied range.
- `btrfs_tree_mod_log_free_eb()` logs removal of all key pointers from an internal extent buffer before it is freed.
- `btrfs_tree_mod_log_rewind()` returns a read-locked extent buffer representing the given block as of `time_seq`, cloning or creating a dummy buffer as needed.
- `btrfs_get_old_root()` and `btrfs_old_root_level()` reconstruct an old root node or root level for a historical sequence.
- `btrfs_tree_mod_log_lowest_seq()` exposes the oldest active blocker sequence.

Core mechanics:
- Each `tree_mod_elem` stores the affected block logical address, a monotonically increasing `seq`, an operation type, slot metadata, and operation-specific payload.
- The log is an rb-tree ordered by logical address and sequence. For a matching logical block, newer sequence entries sort before older ones because insertion descends left when `cur->seq < tm->seq`.
- Logging is skipped when there are no active users, for leaf buffers, and for trees outside the extent tree and filesystem trees. This keeps the log focused on metadata views needed by backref/extent walking.
- Allocation is intentionally done before taking the write lock when possible. After allocation, `tree_mod_dont_log()` rechecks whether logging is still needed while acquiring `tree_mod_log_lock`.
- Logged operations are forward mutations, but rewind applies the inverse: removed key pointers are restored, added key pointers are removed, replaced key pointers are reset to old values, and moves are copied back.
- Root replacement is special: it maps the new root logical address back to the old root logical address/level/generation so callers can follow a chain of root replacements.
- `tree_mod_log_oldest_root()` walks root replacement entries to identify the oldest predecessor relevant for a requested sequence.
- Rewinding a freed internal node may allocate a dummy extent buffer and repopulate it from logged key removals rather than reading the block from disk.

Important invariants:
- Callers must hold/log around structural internal-node mutations before the mutation becomes visible to concurrent old-view readers.
- Only internal nodes are rewound; leaves return unchanged because `skip_eb_logging()` omits level-0 buffers.
- `fs_info->tree_mod_log_lock` protects both the rb-tree and active sequence blocker list.
- Log records older than the minimum active blocker sequence are no longer needed and may be freed.
- `tree_mod_log_rewind()` tracks `max_slot` separately from `nritems` to detect invalid reverse memmoves during move replay.
- Root replacement replay must treat the logged logical address as the new root address while the payload points at the old root.

Filesystem relevance:
- This is a concurrency support layer for Btrfs metadata consistency. It lets long-running backref, extent, and root-history lookups observe a coherent older tree topology while balancing, COW, root promotion, and delayed-ref activity mutate live trees.

Notable risks:
- Missing a log insertion around an internal-node mutation can make old-root/backref reconstruction inconsistent.
- Ordering of multi-entry operations matters; partial insertion failures erase already inserted entries to avoid corrupt rewind state.
- Several paths use `BUG_ON()`, `ASSERT()`, and warnings for impossible or corrupt replay states, so malformed log state can escalate beyond a recoverable error.
- The code deliberately avoids logging many trees and all leaves; changing callers or use cases requires revalidating those skip rules.
