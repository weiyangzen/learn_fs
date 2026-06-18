# File Research: sources/local-fs/xfsprogs/repair/btree.c

## Purpose

`btree.c` implements a small generic in-memory B-tree mapping unsigned long keys to non-null pointer values. It is repair-local and separate from XFS on-disk btree code. It supports lookup, nearest-key find, ordered cursor movement, insertion, deletion, key/value updates, clearing, destruction, and optional statistics.

## Data Model

- Each node stores up to `BTREE_KEY_MAX` keys, currently 7.
- Each node stores up to 8 child/value pointers.
- Leaves store values in `ptrs`; internal nodes store child pointers.
- `struct btree_root` stores root node, tree height, a reusable path cursor, and lookup cache fields.

## Lookup Behavior

`btree_do_search` descends from root to leaf and records the search path in `root->cursor`. `btree_search` uses a small cache: if the requested key lies between the cached previous key and current key, it reuses the cursor.

Public lookup functions include:

- `btree_lookup` for exact key matches.
- `btree_find` for the first key greater than or equal to the requested key.
- `btree_peek_prev` and `btree_peek_next` around the current cursor.
- `btree_lookup_next` and `btree_lookup_prev` to move the active cursor.

## Mutation Behavior

Insertion rejects null values and duplicate keys. If a node is full, the code first tries to shift entries to previous or next siblings, then increases height if needed, then splits.

Deletion removes the leaf key/value, updates parent separator keys if needed, and handles underflow by merging with siblings or redistributing from siblings. Root height can shrink when the top root becomes empty.

## Key Functions

- `btree_insert_item`
- `btree_split`
- `btree_shift_to_prev`
- `btree_shift_to_next`
- `btree_delete_key`
- `btree_delete_node`
- `btree_balance_with_prev`
- `btree_balance_with_next`
- `btree_update_node_key`

## Important Invariants

- Values must be non-null.
- Keys must remain sorted.
- Nodes must stay within max/min occupancy except transiently during mutation.
- Cursor paths must be invalidated after insert/delete.
- Parent separator keys must track the relevant leaf/internal boundary key.
- Tree height is at least one after initialization.

## Repair and Risk Notes

The implementation uses compact fixed-size nodes and explicit sibling operations instead of a generic library. The most complex areas are cursor copying for neighboring nodes, separator key updates during shifts, and deletion underflow handling. There is a likely typo in a stats guard (`#ifdef btree_stats` lowercase) that means one optional statistic counter is not compiled under the normal `BTREE_STATS` symbol, but it does not affect behavior.
