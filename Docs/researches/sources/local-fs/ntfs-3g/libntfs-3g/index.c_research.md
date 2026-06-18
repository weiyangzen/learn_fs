# File Research: sources/local-fs/ntfs-3g/libntfs-3g/index.c

## Role

Implements generic NTFS index handling for B+tree indexes: lookup, insertion, deletion, index block allocation, bitmap management, root-to-allocation growth, split propagation, and in-order traversal.

## Context and Low-Level Helpers

- `ntfs_index_ctx_get()`, `ntfs_index_ctx_put()`, and `ntfs_index_ctx_reinit()` manage `ntfs_index_context`.
- `ntfs_index_entry_mark_dirty()` marks either the resident index root inode or an index block dirty.
- `ntfs_ie_*` helpers navigate, duplicate, insert, delete, and update `INDEX_ENTRY` records.
- `ntfs_ir_lookup()` and `ntfs_ir_lookup2()` locate resident `AT_INDEX_ROOT`.
- `ntfs_ib_read()` and `ntfs_ib_write()` perform MST-protected I/O for `AT_INDEX_ALLOCATION`.

## Validation

- `ntfs_index_block_inconsistent()` validates `INDX` magic, expected VCN, block size, entry offset, index length, and allocated size.
- `ntfs_index_entry_inconsistent()` validates key/data bounds and filename key bounds.

These checks are used by both generic index code and directory lookup/enumeration.

## Lookup

- `ntfs_index_lookup()` sets up the index root, chooses the collation function with `ntfs_get_collate_function()`, searches the root, then descends through index blocks until it finds the key, identifies an insertion point, or reports corruption/error.
- `ntfs_ie_lookup()` performs ordered search inside a single index header and returns whether to keep descending through a child VCN.

## Allocation and Growth

- `ntfs_ibm_add()`, `ntfs_ibm_modify()`, `ntfs_ibm_set()`, `ntfs_ibm_clear()`, and `ntfs_ibm_get_free()` manage the index bitmap.
- `ntfs_ia_add()` creates/open `$INDEX_ALLOCATION` and ensures `$BITMAP` exists.
- `ntfs_ir_to_ib()` copies root entries into a new index block.
- `ntfs_ir_reparent()` converts a small resident index root into a large index rooted at a child block.
- `ntfs_ir_truncate()` and `ntfs_ir_make_space()` resize resident index root storage or trigger reparenting.

## Insert and Split

- `ntfs_ie_add()` is the generic entry insertion routine. It first performs lookup, then inserts into root/block if there is space, otherwise grows root or splits an index block and retries.
- `ntfs_index_add_filename()` builds a filename index entry and inserts it into `$I30`.
- `ntfs_ib_split()` chooses a median, allocates a new block, copies the tail, inserts the median into the parent, and cuts the old block tail.
- `ntfs_ib_insert()` inserts propagated median entries into parent index blocks, splitting parent blocks as needed.
- `ntfs_ir_insert_median()` inserts a propagated median into the root.

## Remove and Rebalance

- `ntfs_index_rm()` removes the entry currently described by an index context.
- `ntfs_index_remove()` wraps lookup plus removal for directory filename indexes.
- `ntfs_index_rm_node()` handles deletion of internal-node entries by replacing with successor data from the leaf side.
- `ntfs_index_rm_leaf()` clears bitmap entries and recursively removes empty leaves.
- `ntfs_ih_takeout()`, `ntfs_ir_leafify()`, and `ntfs_ih_reparent_end()` handle parent cleanup and root shrink/leaf conversion cases.

## Traversal

- `ntfs_index_next()` returns the next index entry in collation order after a lookup-initialized position.
- `ntfs_index_walk_down()` descends to the leftmost leaf under a child pointer.
- `ntfs_index_walk_up()` ascends until it finds a parent data entry or reaches the end.

## Dependencies

Depends on attributes, MST record I/O, bitmap attributes, collation dispatch, directory filename structures, reparse/misc helpers, and logging.

## Important Behavior

Index root is required to be resident. Index allocation blocks are MST-protected `INDX` records. The context stores parent VCN/position stacks with a fixed maximum depth (`MAX_PARENT_VCN`), returning `EOPNOTSUPP` if exceeded.

Insertion and deletion may return `STATUS_KEEP_SEARCHING` to tell callers to reinitialize and retry after structural changes. Dirty index blocks are written on context cleanup if marked dirty.

## Research Notes

This is the generic B+tree engine used directly by `dir.c` for `$I30` and by other NTFS metadata indexes. The main invariants are sorted collation order, valid child VCN pointers, synchronized bitmap allocation, and resident-root versus allocation-block consistency.
