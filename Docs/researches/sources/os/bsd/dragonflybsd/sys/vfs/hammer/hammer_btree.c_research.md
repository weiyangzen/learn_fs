# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.c

This file implements HAMMER’s modified B+Tree search, iteration, insertion, deletion, splitting, removal, mirror-TID propagation, child locking, comparison, and debug printing. The tree stores records only in leaves while internal nodes carry boundary elements that allow cursors to begin searches from cached interior positions instead of always starting at the root.

Core model:
- Internal nodes contain left/right boundary information and subtree pointers.
- Leaf nodes contain record elements only.
- Internal node `count` excludes the right boundary; leaf node `count` is the number of records.
- Searches can start from arbitrary cursor positions and move up/down until the key falls inside current bounds.
- Insertions split full nodes top-down while descending.
- Deletions remove leaf records and may recursively remove empty nodes, but avoid creating empty internal nodes.
- Historical as-of lookup is integrated into the key-search logic through `create_tid` and `delete_tid`.

Traversal and lookup:
- `hammer_btree_lookup()` searches for `cursor->key_beg`, with special handling for `HAMMER_CURSOR_ASOF`.
- `btree_search()` is the core search engine. It moves upward until bounds cover the key, then descends through internal nodes using boundary comparisons and binary-assisted scans.
- `hammer_btree_first()` and `hammer_btree_last()` position cursors for forward or reverse range iteration.
- `hammer_btree_iterate()` advances forward through leaves, moving up/down internal nodes as needed, observing `key_end`, inclusive/exclusive end behavior, ASOF visibility, and mirror-filter skipping.
- `hammer_btree_iterate_reverse()` mirrors forward iteration for reverse scans, especially pruning, without mirror filtering.
- `hammer_btree_search_node()` uses a coarse binary search shortcut before linear checks.

Historical record handling:
- `hammer_btree_cmp()` compares localization, object id, record type, key, and create TID, returning magnitude values that indicate which field differed.
- A create TID of zero sorts as positive infinity.
- `hammer_btree_chkts()` determines whether a record is visible at an as-of TID.
- `btree_search()` can set `HAMMER_CURSOR_CREATE_CHECK` and `cursor->create_check` when an as-of lookup might have descended too far right due to create-TID boundary placement. `hammer_btree_lookup()` retries with the adjusted create TID.

Extraction:
- `hammer_btree_extract()` records the current leaf element in the cursor and optionally reads associated data through `hammer_bread_ext()`.
- Data CRC is verified with `hammer_crc_test_leaf()`.
- CRC failure can return `EDOM` for less-critical mirror-domain transactions or `EIO` otherwise.
- Bulk data buffers can be marked non-metadata to avoid inappropriate metadata treatment.

Insertion:
- `hammer_btree_insert()` requires a cursor previously positioned by an insert-mode lookup returning `ENOENT`.
- It upgrades the cursor node, shifts leaf elements, inserts the new leaf, updates count and cursor tracking, and updates node mirror TID aggregation.
- It returns a propagation hint through `doprop` when the inserted record’s create/delete TID raises the node mirror TID.

Deletion:
- `hammer_btree_delete()` upgrades the cursor, removes the current leaf element, updates cursor tracking, and calls `btree_remove()` if the leaf becomes empty.
- Empty leaf removal may recurse upward. If deadlock prevents full cleanup, empty leaves can remain for later cleanup.
- Deletion tracks optionally how many B-Tree nodes were deleted.

Splitting:
- `btree_split_internal()` splits a full internal node, promotes a separator into the parent, fixes child parent pointers, and creates a new root if splitting the filesystem root.
- `btree_split_leaf()` splits a full leaf, creates a separator between adjacent leaf keys using `hammer_make_separator()`, inserts it into the parent, and creates a new root if needed.
- Split points are normally near half, but append-like insertion at the end uses a three-quarter split heuristic unless the node has been marked nonlinear.
- Splits carefully adjust cursor node/index, parent index, and left/right bounds.

Node removal:
- `btree_remove()` handles deletion of empty leaves or one-element internal nodes.
- Removing the root converts it into an empty leaf.
- For parent count greater than one, it removes the parent’s subtree pointer, preserves mirror TID coverage, updates cursor tracking, deletes the node, and moves the cursor upward.
- For parent count one, it uses `hammer_cursor_up_locked()` and recursive removal, with deadlock-aware fallback.

Mirror support:
- `hammer_btree_do_propagation()` propagates a leaf/node mirror TID upward after modifications, using a pushed cursor so the original cursor can be temporarily unlocked and restored.
- `hammer_btree_mirror_propagate()` updates parent internal elements and node aggregate mirror TIDs until no higher propagation is needed.
- `hammer_cursor_mirror_filter()` computes skipped key ranges when mirroring can skip entire subtrees whose aggregate mirror TID is older than the requested mirror TID.

Recursive child locking and rebalance support:
- `hammer_btree_lock_children()` exclusively locks child subtrees to protect cursor consistency during split/rebalance operations.
- It prefetches children before taking exclusive locks to avoid blocking on I/O while holding locks.
- `hammer_btree_lcache_init()` and `hammer_btree_lcache_free()` preallocate node-lock/cache structures and node copies for deep rebalance operations.
- `hammer_btree_lock_copy()` snapshots locked nodes in memory.
- `hammer_btree_sync_copy()` writes modified copies back to real nodes and deletes nodes marked deleted.
- `hammer_btree_unlock_children()` releases recursive locks and returns cached structures.

Parent/child helpers:
- `hammer_btree_get_parent()` loads and locks a node’s parent, then finds the parent element pointing to the child.
- `btree_set_parent_of_child()` updates a moved child’s parent pointer when internal elements move during splits.
- `btree_node_is_full()` checks type-specific node capacity.

Debug support:
- `hammer_print_btree_node()` and `hammer_print_btree_elm()` dump node and element state.
- Inline debug helpers print cursor, element, parent, key, and comparison information when B-Tree debugging is enabled.

Important invariants:
- Internal elements must have nonzero subtree offsets.
- Leaf elements must be record elements.
- Cursor bounds must contain the selected node and insertion key after splits.
- Empty internal nodes are not allowed.
- Root splitting updates `vol0_btree_root`.
- Modifications use HAMMER node modification helpers so undo/CRC/dirty tracking is preserved.
