# File Research: sources/local-fs/xfsprogs/repair/avl.h

## Purpose

`avl.h` declares the repair-local AVL interval tree API and core node/tree structures.

## Main Types

- `avlnode_t` is the embedded node containing left/right/parent pointers, the in-order `avl_nextino` pointer, and balance state.
- `avlops_t` supplies callbacks to compute a node range start and end.
- `avltree_desc_t` stores the tree root, first in-order node, callback table, and flags.

## Public API

The header declares insertion, deletion, initialization, range lookup, adjacency lookup, range enumeration, and first/last helpers. It also provides inline `avl_findrange` for containing-range lookup.

## Constants

- Balance values: `AVL_BACK`, `AVL_BALANCE`, `AVL_FORW`.
- Tree flag: `AVLF_DUPLICITY`.
- Adjacency directions: `AVL_PRECEED`, `AVL_SUCCEED`.
- Range matching modes: `AVL_INCLUDE_ZEROLEN`, `AVL_EXCLUDE_ZEROLEN`.

## Important Invariants

- Callback-provided ranges are the ordering key.
- `avl_findrange` treats ranges as `[start, end)`.
- The API assumes the caller embeds `avlnode_t` in a structure whose range callbacks are stable while the node is in the tree.

## Research Notes

This is a generic local range-tree interface, not an XFS on-disk btree. It is tuned for repair’s interval tracking and ordered inode/range scans.
