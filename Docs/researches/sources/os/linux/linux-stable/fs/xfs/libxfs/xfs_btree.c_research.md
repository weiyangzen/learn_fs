# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.c

## Role in the repository

`xfs_btree.c` is the generic XFS btree engine. It implements shared cursor navigation, lookup, insert, update, delete, balancing, block verification, query iteration, block ownership changes, cursor cache lifecycle, and inode-rooted metadata btree block allocation helpers. Filesystem-specific btrees such as allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount plug into this core through `struct xfs_btree_ops`.

The implementation supports three btree placement models:
- AG-rooted btrees with short AG block pointers.
- Inode-rooted btrees with long filesystem block pointers and an in-inode root block.
- In-memory xfile-backed btrees used by online repair, with long pseudo block pointers.

## Core abstractions and layout

The file treats every btree block as a `struct xfs_btree_block` header followed by either records for leaf blocks or key/pointer arrays for internal blocks. All record, key, and pointer indexing is one-based, which is reflected in helpers such as `xfs_btree_rec_addr`, `xfs_btree_key_addr`, and `xfs_btree_ptr_addr`.

Block layout and addressing are driven by:
- `xfs_btree_block_len`, which chooses short/long and CRC/non-CRC header length.
- `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset`, which compute field offsets from the ops-provided key, pointer, and record sizes.
- `xfs_btree_get_block`, which returns either an inode-rooted in-fork root block or a buffer-backed block for the requested cursor level.

For overlapping interval btrees, internal nodes store low and high keys per pointer. `xfs_btree_get_leaf_keys`, `xfs_btree_get_node_keys`, `xfs_btree_high_key_from_key`, `__xfs_btree_updkeys`, and `xfs_btree_update_keys` maintain those low/high key summaries. Regular btrees only need parent key updates when the first entry in a child changes; overlapping btrees generally need broader high-key maintenance because the maximum high key can be anywhere in the child.

## Verification and corruption handling

The file contains shared verifiers for long, short, and memory-backed btree blocks:
- `__xfs_btree_check_lblock_hdr`, `__xfs_btree_check_fsblock`, `__xfs_btree_check_memblock`, and `__xfs_btree_check_agblock` validate header magic, level, record count, UUID, block address, padding, and sibling pointers.
- `__xfs_btree_check_block` dispatches verification by btree type.
- `xfs_btree_check_block` converts verifier failures or injected btree check errors into `-EFSCORRUPTED`, traces corrupt buffers, and marks the owning metadata sick.
- `__xfs_btree_check_ptr` and `xfs_btree_check_ptr` validate block pointers against the appropriate address space: in-memory xfile blocks, filesystem blocks, or AG blocks.
- `xfs_btree_check_block_owner` verifies CRC-format owner fields when the caller has enough cursor context to know the expected owner.

The public verifier helpers near the end of the file are used by per-btree buffer verifiers:
- `xfs_btree_fsblock_v5hdr_verify` checks long-format v5 UUID, block number, and optional owner.
- `xfs_btree_fsblock_verify` checks long-format record count and filesystem-block siblings.
- `xfs_btree_memblock_verify` checks xfile-backed record count and xfile sibling pointers.
- `xfs_btree_agblock_v5hdr_verify` checks short-format v5 UUID, block number, and AG owner.
- `xfs_btree_agblock_verify` checks short-format record count and AG-block siblings.

CRC support is split by pointer format:
- `xfs_btree_fsblock_calc_crc` and `xfs_btree_fsblock_verify_crc` handle long-format blocks.
- `xfs_btree_agblock_calc_crc` and `xfs_btree_agblock_verify_crc` handle short-format blocks.

These functions update or validate the LSN and checksum only on CRC-enabled filesystems.

## Cursor lifetime and buffer handling

`xfs_btree_del_cursor` releases buffers attached to each cursor level, drops any held allocation group or realtime group reference, asserts that bmap cursors did not leak unaccounted allocations, and frees the cursor from its cache.

`xfs_btree_dup_cursor` duplicates a cursor by invoking the btree-specific `dup_cursor` callback, copying the current record and per-level cursor state, and re-reading all buffers attached to the source cursor. Staging cursors cannot be duplicated because they are private rebuild cursors. Metadata read failures that indicate sick metadata mark the duplicate cursor sick before unwinding.

`xfs_btree_setbuf` swaps the buffer for a cursor level, releases any previous buffer, resets sibling readahead state, and pre-marks missing left or right siblings as already read-ahead. `xfs_btree_buftarg` and `xfs_btree_bbsize` abstract the target and block size for disk-backed versus memory-backed btrees.

## Block initialization, logging, and primitive moves

`__xfs_btree_init_block`, `xfs_btree_init_block`, `xfs_btree_init_buf`, and `xfs_btree_init_block_cur` initialize btree headers with magic, level, record count, null sibling pointers, owner, UUID, LSN, block number, and buffer ops as appropriate.

The file centralizes transaction logging ranges:
- `xfs_btree_log_keys`, `xfs_btree_log_recs`, and `xfs_btree_log_ptrs` log changed key, record, and pointer ranges.
- `xfs_btree_log_block` logs selected header fields using offset tables for short and long formats. It deliberately avoids logging the CRC field directly because log recovery recreates block checksums.

Low-level movement helpers copy or shift keys, records, and pointers with the sizes supplied by `xfs_btree_ops`. These are used by balancing, splits, joins, insertion, deletion, and bulk root promotion/demotion.

## Lookup and navigation

`xfs_btree_lookup` performs a root-to-leaf binary search using `cmp_key_with_cur`. It handles empty single-leaf trees, exact/equal/less-or-equal/greater-or-equal lookup modes, and cursor positioning after off-block searches. Internal node descent is mediated by `xfs_btree_lookup_get_block`, which reuses a level buffer when possible, reads buffers otherwise, checks owners, verifies expected level, rejects empty internal nodes, and attaches the buffer to the cursor.

`xfs_btree_increment` and `xfs_btree_decrement` move a cursor forward or backward at a given level. They handle movement within the current block, crossing sibling blocks, walking upward to find the next/previous parent pointer, then walking back down to reset lower-level buffers and pointers. The functions issue directional readahead through `xfs_btree_readahead`.

`xfs_btree_goto_left_edge` positions a cursor before the first record by looking up the zero key and then decrementing, validating that the cursor did not land on a real record.

`xfs_btree_has_more_records` tests whether the current leaf has remaining records or a right sibling.

## Insert path

Insertion starts in `xfs_btree_insert`, which builds a leaf record and key from the cursor via btree-specific callbacks, then repeatedly calls `xfs_btree_insrec` from leaf toward root until no split pointer remains.

`xfs_btree_insrec`:
- Rejects insertion when the cursor points off the left edge.
- Checks ordering in debug builds.
- Calls `xfs_btree_make_block_unfull` if the target block is full.
- Inserts either a leaf record or an internal key/pointer by shifting entries right.
- Logs modified records, keys, pointers, and record counts.
- Updates parent keys when needed.
- Propagates split key/pointer state and a replacement cursor upward.

`xfs_btree_make_block_unfull` first tries right shift, then left shift, then split. For an inode-rooted in-fork root, it either expands the in-memory root with `broot_realloc` or promotes it into a real block with `xfs_btree_new_iroot`.

`__xfs_btree_split` allocates a right block, splits entries between old and new blocks, copies leaf records or internal key/pointer pairs, fixes sibling links, updates the right-right sibling if present, updates high keys for overlapping btrees, and returns the new block pointer/key. Kernel builds may route bmap btree splits through `xfs_btree_split_worker` to gain stack space while preserving transaction and reclaim context.

Root growth is split by root type:
- `xfs_btree_new_iroot` promotes an inode fork root into a real child block, handling both leaf roots and node roots.
- `xfs_btree_new_root` allocates a new external root for AG-rooted, memory-rooted, or staged AG btrees after root-level splits.
- `xfs_btree_set_root` updates either a staging fake root or the real btree-specific root callback.

## Update path

`xfs_btree_update` overwrites the current leaf record, logs it, and updates parent keys if the changed record can affect low/high key summaries. This path uses the same key propagation logic as insert/delete, which keeps standard and overlapping btrees consistent through one interface.

## Delete and rebalance path

`xfs_btree_delete` calls `xfs_btree_delrec` from leaf upward while joins require deleting parent key/pointer entries. If joins occurred in an overlapping tree, it force-updates high keys afterward.

`xfs_btree_delrec`:
- Removes a leaf record or internal key/pointer from the current block.
- Shrinks inode-rooted root blocks in memory.
- Collapses roots with a single child via `xfs_btree_kill_iroot` or `xfs_btree_kill_root`.
- Updates parent keys when the deleted entry affects key summaries.
- Accepts blocks that remain above minimum occupancy.
- Otherwise attempts to borrow from right or left siblings with `xfs_btree_lshift` or `xfs_btree_rshift`.
- Joins with a sibling when borrowing cannot fix underflow and combined records fit in one block.
- Fixes sibling pointers, frees the removed block, adjusts the cursor, and signals whether a parent entry must be removed.

Inode-rooted root demotion uses:
- `xfs_btree_demote_leaf_child` to copy child leaf records into the inode root.
- `xfs_btree_demote_node_child` to copy child node key/pointers into the inode root.
- `xfs_btree_kill_iroot` to replace a one-child inode root with the child contents when the child fits.

External-root collapse uses `xfs_btree_kill_root`, which updates the root pointer, frees the old root block, clears the old cursor level, and reduces tree height.

## Tree scanning, owner changes, and query helpers

`xfs_btree_visit_blocks` walks every block level left-to-right, optionally visiting internal and/or leaf levels. It uses sibling pointers and readahead, and `xfs_btree_visit_block` detects a self-referential right sibling to avoid cyclic traversal.

`xfs_btree_change_owner` uses `xfs_btree_visit_blocks` to rewrite owner fields throughout a CRC-format btree. When a transaction is present, it tries ordered buffer logging and can return `-EAGAIN` after logging a buffer normally if ordered logging was not possible. Without a transaction, it queues buffers for delayed write, which is useful in recovery-style contexts.

Range querying is implemented in two modes:
- `xfs_btree_simple_query_range` uses a less-or-equal lookup and forward iteration for non-overlapping btrees.
- `xfs_btree_overlapped_query_range` performs interval-tree-style traversal using low/high keys in internal nodes and leaf records.

`xfs_btree_query_range` converts caller-supplied incore low/high records to keys, validates ordering, and dispatches to the correct query mode. `xfs_btree_query_all` scans all records by using an all-zero low key and all-ones high key.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by iterating matching records and checking contiguity through the btree-specific `keys_contiguous` callback. It supports optional masked comparisons for use cases that intentionally ignore portions of the key.

`xfs_btree_count_blocks` counts all blocks by visiting the whole tree. `xfs_btree_cmp_two_ptrs` compares short or long btree pointers numerically.

## Size and height helpers

The file exposes generic geometry helpers:
- `xfs_btree_compute_maxlevels` computes the height needed for a number of records.
- `xfs_btree_calc_size` computes total btree blocks needed for a number of records.
- `xfs_btree_space_to_height` computes how tall a tree can be with a number of available leaf blocks.

These helpers are parameterized by leaf and node fanout limits.

## Cursor caches and metadata-file blocks

`xfs_btree_init_cur_caches` initializes cursor caches for allocbt, inobt, bmbt, rmapbt, refcountbt, realtime rmapbt, and realtime refcountbt, unwinding through `xfs_btree_destroy_cur_caches` on failure. `xfs_btree_destroy_cur_caches` destroys all those caches.

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate and free one block for inode-rooted metadata btrees. They require a metadata directory inode, use metadata-file AG reservation accounting, set rmap owner info for the inode/fork, and update metadata-file reserved space counters.

## Important invariants

- Btree block entries are one-based, not zero-based.
- Staging cursors cannot use normal allocation, freeing, duplication, query, or modification paths except through the staging bulk-loader interface.
- Inode-rooted btrees may have their root in the inode fork, so root-level functions must tolerate `bp == NULL`.
- Overlapping btrees require high-key maintenance after updates, shifts, splits, joins, and deletions.
- Internal nodes must not be empty; the code treats empty non-root internal blocks as corruption.
- CRC-format owner checks may be skipped for bmap extent-swap scenarios through `XFS_BTREE_BMBT_INVALID_OWNER`.
- Buffer logging for btree blocks records changed byte ranges but not checksum fields directly.

## Dependencies and callers

This file depends on XFS transaction, buffer, allocation, health, trace, rmap, metadata inode, xfile/memory buffer, and per-btree headers. Its exported functions are consumed by the concrete XFS btree implementations and by repair/scrub code that needs generic traversal, range queries, owner changes, and staging support.
