# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree.c

## Purpose

`xfs_btree.c` is the generic XFS btree engine used by xfsprogs libxfs. It implements shared block verification, cursor movement, lookup, insert, update, delete, balancing, split/join, block traversal, range query, owner rewrite, geometry calculation, cursor-cache setup, and inode-rooted metadata btree block allocation helpers.

Concrete XFS btrees such as allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount plug into this engine through `struct xfs_btree_ops`.

This xfsprogs copy is the userspace libxfs version. Compared with the Linux kernel copy in this repository, the meaningful local difference in this file is the include environment: xfsprogs uses `xfs_platform.h`, `xfile.h`, and `buf_mem.h`, and omits kernel-only include dependencies such as log and quota internals. Kernel-only split worker code remains guarded by `#ifdef __KERNEL__`, so xfsprogs uses the direct split path.

## Block Model

The file treats all btree blocks as `struct xfs_btree_block` headers followed by either:

- leaf records, addressed by `xfs_btree_rec_addr`;
- internal low keys, optional high keys, and child pointers, addressed by `xfs_btree_key_addr`, `xfs_btree_high_key_addr`, and `xfs_btree_ptr_addr`.

All in-block record/key/pointer indexes are one-based.

The block header length depends on pointer format and CRC format:

- long pointer btrees use long-format headers for filesystem block or xfile block pointers;
- short pointer btrees use allocation-group block pointers;
- CRC-enabled filesystems use extended v5 headers with UUID, block number, owner, LSN, and CRC fields.

`xfs_btree_block_len`, `xfs_btree_rec_offset`, `xfs_btree_key_offset`, `xfs_btree_high_key_offset`, and `xfs_btree_ptr_offset` centralize this layout math.

## Btree Types

The generic code dispatches on `cur->bc_ops->type`:

- `XFS_BTREE_TYPE_AG`: short-pointer AG-rooted btrees.
- `XFS_BTREE_TYPE_INODE`: long-pointer inode-rooted btrees with roots stored in inode forks.
- `XFS_BTREE_TYPE_MEM`: long-pointer in-memory xfile-backed btrees used by repair/staging workflows.

Helpers such as `xfs_btree_buftarg`, `xfs_btree_bbsize`, `xfs_btree_ptr_to_daddr`, `xfs_btree_buf_to_ptr`, and pointer verification routines abstract these address spaces.

## Verification and Corruption Handling

The top of the file implements btree block and pointer verification.

Header checks include:

- magic number via `xfs_btree_magic`;
- expected level;
- maximum record count for the level;
- CRC-format metadata UUID;
- buffer disk address;
- owner fields when enough cursor context exists;
- long-format padding;
- sibling pointers.

Sibling pointer checks reject self-references and out-of-range addresses. Separate helpers cover filesystem block siblings, memory-backed xfile siblings, and AG block siblings.

Main verification entry points:

- `__xfs_btree_check_block`
- `xfs_btree_check_block`
- `__xfs_btree_check_ptr`
- `xfs_btree_check_ptr`
- `xfs_btree_check_block_owner`
- `xfs_btree_fsblock_v5hdr_verify`
- `xfs_btree_fsblock_verify`
- `xfs_btree_memblock_verify`
- `xfs_btree_agblock_v5hdr_verify`
- `xfs_btree_agblock_verify`

On verifier failure, the code marks the btree sick through health reporting, marks corrupt buffers where applicable, traces corruption, and returns `-EFSCORRUPTED`.

## CRC Helpers

The file provides btree-specific wrappers around buffer checksum logic:

- `xfs_btree_fsblock_calc_crc`
- `xfs_btree_fsblock_verify_crc`
- `xfs_btree_agblock_calc_crc`
- `xfs_btree_agblock_verify_crc`

For CRC filesystems, these helpers validate log sequence numbers and update/verify CRC fields at the correct long- or short-header offsets. When calculating CRCs, the LSN is copied from the buffer log item if available.

## Cursor Lifecycle

`xfs_btree_del_cursor` releases cursor buffers, drops held group references, checks bmap allocation accounting, and frees the cursor from its cache.

`xfs_btree_dup_cursor` duplicates a cursor by calling the concrete btree `dup_cursor` operation, copying cursor record and level state, and re-reading each attached buffer. Staging cursors cannot be duplicated because staged rebuild cursors are intended to be private.

`xfs_btree_setbuf` swaps a cursor-level buffer, releases any old buffer, clears readahead state, and records when left or right sibling readahead is unnecessary because the sibling pointer is null.

## Buffer and Block Initialization

The file initializes headers through:

- `__xfs_btree_init_block`
- `xfs_btree_init_block`
- `xfs_btree_init_buf`
- `xfs_btree_init_block_cur`

These functions set magic, level, record count, null siblings, block number, owner, UUID, LSN, and buffer ops.

`xfs_btree_owner` computes the expected owner from the btree type:

- memory btrees use `xfbtree->owner`;
- inode btrees use the inode number;
- AG btrees use the group number.

## Logging Helpers

Changes are logged by field and region:

- `xfs_btree_log_keys`
- `xfs_btree_log_recs`
- `xfs_btree_log_ptrs`
- `xfs_btree_log_block`

For inode-rooted in-fork roots, logging maps to inode fork-root log flags. For buffer-backed blocks, logging marks buffers as btree buffers and logs byte ranges. CRC fields are intentionally not logged directly because recovery regenerates checksums.

## Lookup and Cursor Movement

`xfs_btree_lookup` performs root-to-leaf binary search using btree-specific `cmp_key_with_cur`. It supports exact, less-or-equal, and greater-or-equal searches, handles empty single-leaf trees, and fixes cursor positioning when a GE lookup lands beyond the current block but a right sibling exists.

`xfs_btree_lookup_get_block` reads or reuses the block for a level, validates owner and level, rejects empty internal nodes, and attaches the buffer to the cursor.

`xfs_btree_increment` and `xfs_btree_decrement` move a cursor forward or backward at any level. They handle in-block movement, sibling crossing, upward parent-pointer adjustment, downward buffer reloads, and directional sibling readahead.

`xfs_btree_goto_left_edge` positions a cursor before the first record by looking up the zero key and decrementing.

`xfs_btree_has_more_records` reports whether the current leaf has further records or a right sibling.

## Key Propagation

For regular btrees, parent keys need updates mainly when the first record/key in a child changes.

For overlapping interval btrees, internal nodes carry both low and high key summaries. The high key can come from any child record, so the core must recompute and propagate high-key summaries more aggressively.

Important helpers:

- `xfs_btree_high_key_from_key`
- `xfs_btree_get_leaf_keys`
- `xfs_btree_get_node_keys`
- `xfs_btree_get_keys`
- `xfs_btree_needs_key_update`
- `__xfs_btree_updkeys`
- `xfs_btree_updkeys_force`
- `xfs_btree_update_keys`

## Insert Path

`xfs_btree_insert` builds a record and key from the cursor, then repeatedly calls `xfs_btree_insrec` from leaf toward root until no split pointer remains.

`xfs_btree_insrec`:

- validates cursor location;
- makes full blocks non-full;
- shifts keys/pointers or records to open an insertion slot;
- copies the new entry;
- logs changed ranges and record counts;
- propagates key changes;
- returns split information to the next level.

`xfs_btree_make_block_unfull` tries, in order:

1. expand or promote an inode-rooted in-fork root;
2. shift one entry to the right sibling;
3. shift one entry to the left sibling;
4. split the block.

`__xfs_btree_split` allocates a right sibling, divides records/keyptrs between left and right blocks, fixes sibling links, updates neighboring sibling backpointers, computes the new block key, and may create a duplicate cursor for parent insertion.

In xfsprogs builds, `xfs_btree_split` is a direct alias for `__xfs_btree_split`; the kernel-only worker-thread split path is excluded.

## Root Promotion

Inode-rooted btrees can start with a root stored directly in the inode fork. When that root cannot grow further:

- `xfs_btree_new_iroot` allocates a real btree block and copies root contents into it.
- `xfs_btree_promote_leaf_iroot` promotes a leaf root into a node root pointing at a new child block.
- `xfs_btree_promote_node_iroot` promotes a node root by copying key/pointer entries into a child and increasing tree height.

External-root btrees use `xfs_btree_new_root` after a root split. Staging cursors update fake roots through `xfs_btree_set_root`.

## Update Path

`xfs_btree_update` overwrites the current leaf record, logs the record range, and updates parent keys if the modified position can affect low/high key summaries.

This gives regular and overlapping btrees a shared update path while preserving interval-tree high-key correctness.

## Delete and Rebalance Path

`xfs_btree_delete` repeatedly calls `xfs_btree_delrec` from leaf upward while joins require removal of parent key/pointer entries.

`xfs_btree_delrec`:

- removes the selected record or key/pointer;
- shifts remaining entries left;
- decrements and logs record count;
- shrinks inode-rooted roots where possible;
- collapses external roots with one child;
- updates parent keys when needed;
- returns early if the block remains above minimum occupancy;
- attempts single-record rebalancing from right or left siblings;
- joins with a sibling when rebalancing is insufficient;
- frees the removed block.

For overlapping btrees, if block joins occurred, `xfs_btree_delete` force-updates high keys after the upward deletion sequence.

Root collapse helpers:

- `xfs_btree_demote_leaf_child`
- `xfs_btree_demote_node_child`
- `xfs_btree_kill_iroot`
- `xfs_btree_kill_root`

## Traversal and Owner Rewrite

`xfs_btree_visit_blocks` walks every btree level left-to-right using sibling pointers. It supports visiting internal levels, leaf levels, or both. `xfs_btree_visit_block` detects self-referential right siblings to avoid cyclic traversal.

`xfs_btree_change_owner` uses the visitor to rewrite owner fields throughout CRC-format btrees. With a transaction, it uses ordered buffer logging where possible and can return `-EAGAIN` when a normal log is needed. Without a transaction, it queues buffers for delayed write.

## Range Queries

The file supports both ordinary sorted btrees and overlapping interval btrees.

`xfs_btree_query_range` converts incore low/high records to keys, validates ordering, and dispatches to:

- `xfs_btree_simple_query_range` for non-overlapping btrees;
- `xfs_btree_overlapped_query_range` for interval btrees.

The simple query uses LE lookup and forward iteration. The overlapped query performs depth-first traversal using internal low/high key summaries to prune subtrees.

`xfs_btree_query_all` scans all records using all-zero and all-ones key bounds.

`xfs_btree_has_records` classifies a key range as empty, sparse, or full by querying matching records and testing key contiguity through the concrete btree callback. It supports masked key comparisons for callers that intentionally ignore parts of the key.

## Geometry and Sizing

The file provides common sizing helpers:

- `xfs_btree_compute_maxlevels`
- `xfs_btree_calc_size`
- `xfs_btree_space_to_height`

These calculate tree height and block consumption from per-level fanout limits.

## Cursor Cache Initialization

`xfs_btree_init_cur_caches` initializes cursor caches for allocation, inode allocation, bmap, rmap, refcount, realtime rmap, and realtime refcount btrees. On failure it unwinds through `xfs_btree_destroy_cur_caches`.

`xfs_btree_destroy_cur_caches` destroys all these caches.

## Metadata-File Block Helpers

`xfs_btree_alloc_metafile_block` and `xfs_btree_free_metafile_block` allocate and free one block for inode-rooted metadata btrees. They require a metadata directory inode, use metadata-file AG reservation accounting, set rmap owner information for the inode/fork, and update metadata-file reserved space counters.

## Dependencies

This file depends heavily on:

- `xfs_btree.h` for cursor, ops, keys, records, and exported APIs;
- concrete btree modules for ops and cursor caches;
- transaction and buffer APIs;
- xfsprogs xfile/memory-buffer support for in-memory btrees;
- health reporting for sick metadata;
- staging fake-root APIs from `xfs_btree_staging.h`.
