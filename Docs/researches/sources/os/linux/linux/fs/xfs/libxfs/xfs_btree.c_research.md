# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.c

## Purpose

`xfs_btree.c` is the generic XFS btree core. It implements shared cursor traversal, lookup, insert, update, delete, block splitting/joining, root growth/shrink, validation, CRC helpers, query iteration, block visitation, ownership changes, cursor cache lifecycle, and generic block allocation helpers for inode-rooted metadata btrees.

This file is not a concrete btree type by itself. Concrete btrees such as allocbt, inobt, bmbt, rmapbt, refcountbt, realtime rmap/refcount btrees, and in-memory repair btrees provide `struct xfs_btree_ops` callbacks for key comparison, record encoding, allocation/freeing, root updates, and geometry. The core then performs all common structural operations.

## Btree Types Supported

The code dispatches on `cur->bc_ops->type`:

- `XFS_BTREE_TYPE_AG`: short-pointer btrees rooted in allocation group metadata, using AG block pointers.
- `XFS_BTREE_TYPE_INODE`: long-pointer btrees rooted in an inode fork, with the root possibly stored directly inside `if_broot`.
- `XFS_BTREE_TYPE_MEM`: long-pointer btrees backed by in-memory `xmbuf` buffer targets for online repair.

Pointer conversion, sibling verification, block target selection, block size selection, owner derivation, and root handling all branch on this type.

## Major Responsibilities

- Decode btree magic numbers from buffer verifier ops.
- Verify btree block headers, owner fields, sibling pointers, CRC metadata, and child pointers.
- Calculate CRCs for long-format and short-format btree blocks.
- Allocate, duplicate, and delete btree cursors.
- Calculate record, key, high-key, and pointer offsets inside btree blocks.
- Read, cache, release, and readahead btree buffers.
- Handle null pointer encoding for short and long pointer formats.
- Initialize btree blocks and buffers with correct owner, UUID, LSN, magic, level, and sibling fields.
- Log block headers, records, keys, and pointers into the current transaction.
- Traverse records forward and backward with `xfs_btree_increment` and `xfs_btree_decrement`.
- Lookup records with binary search at each level.
- Update records and propagate low/high key changes upward.
- Rebalance via left and right shifts.
- Split full blocks and create new roots.
- Insert records and propagate split pointers upward.
- Delete records, borrow from siblings, join blocks, and collapse roots.
- Visit all btree blocks level-by-level.
- Change btree block owner fields with ordered buffer logging.
- Run range queries for ordinary and overlapping-interval btrees.
- Classify a key range as empty, sparse, or fully packed.
- Compute btree height and block-count geometry from fanout limits.
- Initialize and destroy all btree cursor slab caches.
- Allocate/free blocks for inode-rooted metadata btrees.

## Key Data and Layout Model

The implementation treats btree blocks generically:

- Leaf blocks contain a common header followed by records.
- Internal blocks contain a common header followed by keys and then child pointers.
- Overlapping btrees store low and high keys for each pointer; high keys are addressed by offsetting halfway into the key storage area.

The helper family around `xfs_btree_block_len`, `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset` centralizes this layout. Public address helpers expose typed pointers:

- `xfs_btree_rec_addr`
- `xfs_btree_key_addr`
- `xfs_btree_high_key_addr`
- `xfs_btree_ptr_addr`

All btree entry indexes are one-based, which is a core invariant throughout lookup, insert, delete, shifts, splits, and logging.

## Verification and Corruption Handling

The file contains layered verification:

- Header verification checks magic, level, `numrecs`, metadata UUID, block address, padding, and sibling pointers.
- Long-format filesystem-block siblings are validated as filesystem block numbers.
- Short-format AG-block siblings are validated against the current per-AG.
- In-memory siblings are validated against the `xmbuf` target.
- Child pointers are checked through `__xfs_btree_check_ptr`.
- Owner fields are verified during cursor-driven reads because not every buffer verifier has enough context.
- CRC verify helpers check v5 LSN and buffer checksum state before accepting CRC-format blocks.

Corruption reports mark the associated btree sick via `xfs_btree_mark_sick` and return `-EFSCORRUPTED`. Debug builds add extra pointer, order, and block checks along traversal and modification paths.

## Cursor Lifecycle

`xfs_btree_del_cursor` releases buffers held in `bc_levels`, drops any held group reference, checks bmap allocation accounting, and frees the cursor from its cache.

`xfs_btree_dup_cursor` clones cursor state and rereads every held buffer through the transaction. Staging cursors cannot be duplicated because staged rebuild state is intended to be private. Duplicated cursors are used heavily during sibling shifts and deletion rebalancing so parent paths can be updated without disturbing the primary cursor.

`xfs_btree_init_cur_caches` and `xfs_btree_destroy_cur_caches` initialize/destroy cursor caches for all concrete btree families.

## Lookup and Traversal

`xfs_btree_lookup` starts at the root, initializes a root pointer through `xfs_btree_init_ptr_from_cur`, reads each level with `xfs_btree_lookup_get_block`, binary-searches keys or synthesized leaf keys, and descends through the selected child pointer. It supports `XFS_LOOKUP_EQ`, `XFS_LOOKUP_LE`, and `XFS_LOOKUP_GE`, adjusting the final leaf cursor as needed.

`xfs_btree_increment` and `xfs_btree_decrement` advance a cursor at any level. If the movement stays within the current block, they only adjust the level pointer. If it crosses a block edge, they walk upward to find the next parent pointer and then walk back down, reading child blocks and resetting lower-level positions. They also issue sibling readahead.

`xfs_btree_goto_left_edge` positions the cursor before the first record by performing a low lookup and decrementing once.

## Key Propagation

The file maintains parent keys through:

- `xfs_btree_get_leaf_keys`
- `xfs_btree_get_node_keys`
- `xfs_btree_get_keys`
- `xfs_btree_update_keys`
- `xfs_btree_updkeys_force`

For ordinary btrees, parent keys usually need updating only when the first record/key of a block changes. For overlapping btrees, the highest key might be anywhere in the child subtree, so updates must recalculate and propagate both low and high key information more aggressively.

## Insert Path

`xfs_btree_insert` builds a record from the cursor through `init_rec_from_cur`, derives its key, and calls `xfs_btree_insrec` from the leaf upward until no split pointer remains.

Insertion behavior:

- If the target block has space, make a hole and copy in the new record or key/pointer.
- If the block is full, `xfs_btree_make_block_unfull` tries right shift, left shift, then split.
- If a split reaches the top of an AG/memory-rooted tree, `xfs_btree_new_root` creates a new root.
- If an inode-rooted root cannot grow inside the fork, `xfs_btree_new_iroot` promotes the inline root contents into a real block.
- Parent keys are updated unless the split result key must be propagated to the next level.

BMBT splits can be offloaded to a workqueue in kernel builds to avoid deep stack use, with care to avoid AGF/workqueue deadlocks.

## Delete Path

`xfs_btree_delete` calls `xfs_btree_delrec` from the leaf upward while joins require deleting parent key/pointer entries.

Deletion behavior:

- Remove a record or key/pointer by shifting later entries left.
- Shrink inode fork roots through `broot_realloc`.
- Collapse a root with one child through `xfs_btree_kill_root` or `xfs_btree_kill_iroot`.
- If a non-root block remains above minimum occupancy, finish.
- Otherwise try borrowing one entry from the right or left sibling.
- If borrowing cannot fix occupancy, join with a sibling, free the removed block, fix sibling links, and propagate deletion upward.
- For overlapping btrees, forced key updates are performed after joins.

The deletion path is careful about cursor consistency after joins, especially when the current block is merged into its left neighbor or when parent pointers must advance.

## Root Handling

The code has separate paths for externally rooted and inode-rooted trees:

- `xfs_btree_set_root` updates either the concrete btree root callback or a staging fake root.
- `xfs_btree_new_root` creates a new external root block after a root split.
- `xfs_btree_new_iroot` copies an inode root into a newly allocated real block when the inline root no longer fits.
- `xfs_btree_promote_leaf_iroot` and `xfs_btree_promote_node_iroot` convert inline root contents into child blocks.
- `xfs_btree_kill_iroot`, `xfs_btree_demote_leaf_child`, and `xfs_btree_demote_node_child` collapse inode-rooted btrees back into the fork when possible.

## Query and Scan Facilities

`xfs_btree_query_range` converts in-core low/high records to keys and dispatches:

- Ordinary btrees use `xfs_btree_simple_query_range`, which starts near the low key and walks forward until keys pass the high key.
- Overlapping btrees use `xfs_btree_overlapped_query_range`, which performs interval-tree-style descent using node low/high keys and invokes a callback for overlapping records.

`xfs_btree_query_all` scans the full keyspace.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by querying records and checking key contiguity. It detects illegal overlap for btrees that do not permit overlapping intervals.

`xfs_btree_has_more_records` checks whether the current leaf has more entries or a right sibling.

## Block Visitation and Owner Changes

`xfs_btree_visit_blocks` visits levels from root to leaves, walking each level left-to-right through sibling pointers. It can visit internal blocks, record blocks, or all blocks. It contains a loop-prevention check against a right sibling pointer referencing the current block.

`xfs_btree_change_owner` uses this walker to update owner fields in every block. With a transaction it uses ordered buffer logging and may ask the caller to roll via `-EAGAIN`; without a transaction it queues buffers for delayed write.

## Geometry Helpers

The file provides:

- `xfs_btree_compute_maxlevels`: height required for a record count.
- `xfs_btree_calc_size`: total blocks required for a record count.
- `xfs_btree_space_to_height`: height that can be supported by a given number of leaf blocks.

These are generic fanout calculations used by concrete btree setup and sizing code.

## Metadata Btree Block Helpers

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate/free blocks for inode-rooted metadata btrees. They integrate with metadata-directory inode checks, rmap owner setup, metafile reservation accounting, and deferred free handling.

## Integration Points

This file depends on:

- Concrete btree operation tables in XFS alloc, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount code.
- Transaction buffer read/get/log/release APIs.
- XFS buffer verifiers and CRC helpers.
- Per-AG/per-group references.
- Inode fork handling for inode-rooted btrees.
- Online repair staging and in-memory btree support.
- Health reporting through sick masks.
- Error-tag based fault injection.

## Important Invariants

- Cursor level arrays must match `bc_nlevels`.
- Entry indexes are one-based.
- Staging cursors must not use regular allocation/free/modification paths except bulk loading.
- Inode-rooted root blocks may have no buffer pointer.
- Non-root internal nodes must not be empty.
- Parent low/high keys must describe child subtree contents.
- Sibling pointers must not point to self and must reference valid blocks.
- Root collapse/growth must keep cursor height and root storage synchronized.
