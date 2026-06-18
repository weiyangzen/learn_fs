# File Research: sources/local-fs/xfsprogs/repair/avl.c

## Purpose

`avl.c` implements a repair-local AVL interval tree. Nodes describe ordered half-open ranges via callbacks supplied in `avlops_t`, and the tree maintains both AVL parent/child links and a separate in-order `avl_nextino` chain for fast sequential scans.

This structure is used by repair code that needs range lookup, adjacency lookup, insertion, deletion, and ordered traversal of non-overlapping intervals.

## Main Operations

- `avl_init_tree` initializes a descriptor with root, first node, and range callbacks.
- `avl_insert` inserts a non-overlapping range and rebalances the tree.
- `avl_insert_immediate` inserts a node immediately after a known node.
- `avl_delete` removes a node and rebalances upward.
- `avl_find` finds a node by exact start value.
- `avl_findrange` is an inline header helper that finds the range containing a value.
- `avl_findanyrange` finds any range intersecting a requested range.
- `avl_findadjacent` finds a containing, predecessor, or successor range.
- `avl_findranges` returns the first and last nodes intersecting a range.
- `avl_firstino` and `avl_lastino` find leftmost and rightmost nodes.

## Data Structure Behavior

Each `avlnode_t` stores:

- `avl_back` for the left child.
- `avl_forw` for the right child.
- `avl_parent` for upward navigation.
- `avl_nextino` for in-order iteration.
- `avl_balance` as `AVL_BACK`, `AVL_BALANCE`, or `AVL_FORW`.

The tree descriptor stores root, first in-order node, callback operations, and flags. Range comparison is driven by `AVL_START(tree, node)` and `AVL_END(tree, node)`, allowing callers to embed AVL nodes inside larger structures.

## Balancing Logic

Insertion uses `avl_insert_find_growth` to locate a non-overlapping insertion point and `avl_insert_grow` to attach the node and fix the in-order chain. `avl_balance` then performs single or double rotations.

Deletion handles degenerate one-child cases and two-child replacement with the greatest lesser descendant. `retreat` propagates height shrinkage upward and performs single or double rotations as needed.

## Debug Support

When `AVL_DEBUG` is enabled, `avl_checknode` and `avl_checktree` assert ordering, parent pointers, balance state, and `nextino` consistency. There is also a disabled `STAND_ALONE_DEBUG` interactive test harness.

## Important Invariants

- Ranges are half-open `[start, end)`.
- Non-zero-length ranges must not overlap existing ranges.
- `avl_firstino` must point to the leftmost node.
- `avl_nextino` must preserve sorted order and terminate at `NULL`.
- Parent pointers must match child links after every rotation.
- Balance values must correspond to actual child presence.

## Repair and Risk Notes

The code is pointer-heavy and predates modern container abstractions. The highest-risk sections are delete replacement, `nextino` maintenance, and rotation parent rewiring. Because range start/end are callback-derived, caller bugs in those callbacks can break all ordering assumptions.
