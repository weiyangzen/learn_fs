# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree.h

## Purpose
Public rbtree API and inline helper layer.

## Key Interfaces
- Basic macros: `rb_parent`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, `RB_CLEAR_NODE`.
- Core declarations for insert/erase/traversal/replacement.
- `rb_link_node()` for caller-managed insertion.
- Cached-leftmost helpers: `rb_first_cached`, `rb_insert_color_cached`, `rb_erase_cached`, `rb_replace_node_cached`.
- Generic inline helpers: `rb_add`, `rb_add_cached`, `rb_find_add`, `rb_find`, `rb_find_first`, `rb_next_match`, `rb_for_each`.
- Postorder safe iteration macro.

## Dependencies
Includes `kerncompat.h` and `rbtree_types.h`, with flat and installed include path variants.

## Notable Behaviors
- The API deliberately avoids generic callbacks for core search/insert in performance-sensitive paths; callers usually write their own comparison logic.
- `rb_find_first()` plus `rb_next_match()` supports duplicate-equivalent keys when the comparator groups multiple nodes.

## Risks
- Comparator consistency is critical; partial orders may return any equivalent node except where first-match helpers are used.
- `rbtree_postorder_for_each_entry_safe()` allows freeing the current entry but cannot tolerate tree rebalancing during iteration.
