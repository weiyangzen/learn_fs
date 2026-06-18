# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.c

This debug file implements Btrfs reference verification for the `REF_VERIFY` mount option under `CONFIG_BTRFS_DEBUG`. It builds an in-memory model of extent-tree references at mount time, updates that model as delayed refs are modified, and disables reference verification if it detects inconsistency or cannot maintain the model.

Private data model:
- `struct block_entry` represents one referenced block by bytenr/length. It records total refs, metadata/data classification, whether it came from disk, per-root direct ref counts, detailed refs, and a list of historical actions.
- `struct root_entry` tracks how many direct refs one root has for a block.
- `struct ref_entry` describes one expected extent-tree reference by `root_objectid`, `parent`, `owner`, `offset`, and `num_refs`.
- `struct ref_action` records each delayed-ref action applied to a block, including the action, real root, a copy of the ref fields, list node, and optional stack trace.

Tree indexing:
- `fs_info->block_tree` is keyed by block bytenr and protected by `fs_info->ref_verify_lock`.
- Each `block_entry` has a `roots` red-black tree keyed by root objectid and a `refs` red-black tree keyed by the full ref tuple.
- `block_entry_bytenr_*`, `root_entry_root_objectid_*`, `comp_refs()`, and `ref_entry_cmp()` implement the ordering.
- `insert_block_entry()`, `lookup_block_entry()`, `insert_root_entry()`, `lookup_root_entry()`, and `insert_ref_entry()` are the local rb-tree primitives.

Mount-time model construction:
- `btrfs_build_ref_tree()` is called after the extent tree is available. It reads and locks the root node, walks the entire extent tree, and populates `fs_info->block_tree`.
- `walk_down_tree()` descends from the current internal node to leaves with read locks.
- `walk_up_tree()` releases nodes and advances to the next subtree.
- `process_leaf()` iterates leaf items and dispatches extent items, metadata items, tree block refs, shared block refs, extent data refs, and shared data refs.
- `process_extent_item()` parses inline refs inside extent or metadata items, including tree block refs, shared block refs, extent data refs, shared data refs, and simple-quota owner refs.
- `add_tree_block()`, `add_extent_data_ref()`, and `add_shared_data_ref()` add refs found on disk into the in-memory model.

Delayed-ref update verification:
- `btrfs_ref_tree_mod()` is the main update hook. `extent-tree.c` calls it when delayed refs are added or dropped.
- It ignores work unless the `REF_VERIFY` mount option is active.
- It normalizes a `struct btrfs_ref` into a `ref_entry`: metadata refs use tree level as owner, data refs use objectid/offset, and shared refs use `parent`.
- For `BTRFS_ADD_DELAYED_EXTENT`, it creates or finds a block entry, increments total refs, marks metadata when appropriate, and verifies that a newly allocated block does not already have live refs.
- For ordinary add/drop delayed refs, it looks up the existing block, inserts root tracking for direct refs, inserts or updates the detailed ref, rejects dropping nonexistent refs, rejects over-dropping, and rejects adding duplicate tree-block refs.
- It adjusts `block_entry::num_refs` and root-entry counts for `BTRFS_ADD_DELAYED_REF` / `BTRFS_DROP_DELAYED_REF`.
- It appends a `ref_action` history entry on success; on failure it dumps diagnostic state, frees the ref cache, and clears `REF_VERIFY`.

Diagnostics:
- `__save_stack_trace()` and `__print_stack_trace()` capture and print action stack traces when `CONFIG_STACKTRACE` is available.
- `dump_ref_action()` logs one action’s operation, real root, ref root, parent, owner, offset, and ref count.
- `dump_block_entry()` logs all refs, roots, and action history for a block.
- Error messages target conditions such as reallocating a referenced block, dropping a nonexistent ref, finding duplicate on-disk refs, missing root entries, and block entries overlapping a freed range.

Cache cleanup:
- `free_block_entry()` releases roots, refs, actions, and the block entry itself.
- `btrfs_free_ref_cache()` frees the whole model at unmount or after verification failure.
- `btrfs_free_ref_tree_range()` removes all block entries contained in a freed block-group range and logs entries that overlap the range boundaries.

Cross-file relationships:
- `disk-io.c` initializes the verifier lock/tree with `btrfs_init_ref_verify()`, builds the ref tree during mount, and frees it during cleanup.
- `extent-tree.c` calls `btrfs_ref_tree_mod()` from delayed-ref and extent-allocation/freeing paths.
- `block-group.c` calls `btrfs_free_ref_tree_range()` when a block group range is removed.
- `super.c` parses and reports the `REF_VERIFY` mount option.
- `ref-verify.h` compiles these hooks to no-ops outside `CONFIG_BTRFS_DEBUG`.

Important invariants and risks:
- `add_block_entry()` returns with `fs_info->ref_verify_lock` held on success or existing-entry return; callers are responsible for unlocking in those flows.
- The model intentionally persists block action history until unmount, except when a block is successfully reallocated with zero live refs and old actions are discarded.
- Direct refs update both detailed refs and root-entry counts; shared refs do not have a root entry.
- `metadata = owner < BTRFS_FIRST_FREE_OBJECTID` drives duplicate-ref rules, so correct owner normalization is essential.
- The extent-tree walker carries the last `bytenr`, `num_bytes`, and `tree_block_level` across items because separate ref-key items can follow an extent item on later leaves.
- Any verification error disables `REF_VERIFY` rather than continuing with a suspect model.
