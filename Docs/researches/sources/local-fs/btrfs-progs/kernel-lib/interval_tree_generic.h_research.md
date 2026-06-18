# File Research: sources/local-fs/btrfs-progs/kernel-lib/interval_tree_generic.h

## Purpose
Macro template for generating augmented red-black interval-tree implementations.

## Key Interface
- `INTERVAL_TREE_DEFINE(...)` emits prefixed insert/remove/search/iteration functions for a caller-provided node type and interval endpoint accessors.

## Generated Behavior
- Maintains an augmented `ITSUBTREE` field containing the maximum interval end in each subtree.
- Inserts nodes ordered by interval start.
- Removes nodes through `rb_erase_augmented()`.
- Supports `iter_first(root, start, last)` and `iter_next(node, start, last)` over intervals intersecting `[start, last]`.

## Dependencies
Uses `kernel-lib/rbtree_augmented.h`.

## Risks
- This is a macro code generator; correctness depends on caller-supplied `ITSTART`, `ITLAST`, field names, and update discipline.
- It assumes closed intervals and requires the caller’s endpoint type comparisons to be valid for all represented ranges.
