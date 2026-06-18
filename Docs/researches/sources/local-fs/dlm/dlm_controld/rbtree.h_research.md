# File Research: sources/local-fs/dlm/dlm_controld/rbtree.h

This is a userspace copy of Linux `include/linux/rbtree.h`. It declares rb-tree APIs and provides inline helper algorithms.

Key contents:
- Includes `linux_helpers.h` and `rbtree_types.h`.
- Defines `rb_parent`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, and `RB_CLEAR_NODE`.
- Declares core exported functions from `rbtree.c`.
- Defines `rb_link_node()`.
- Provides cached-root helpers: `rb_first_cached`, `rb_insert_color_cached`, `rb_erase_cached`, `rb_replace_node_cached`.
- Provides generic inline helpers: `rb_add_cached`, `rb_add`, `rb_find_add`, `rb_find`, `rb_find_first`, `rb_next_match`, and `rb_for_each`.
- Provides postorder safe iteration macro `rbtree_postorder_for_each_entry_safe`.

Used by:
- `plock.c` resource indexing.
- `rbtree_augmented.h` and `rbtree.c`.

Important constraints:
- Users provide their own comparison/search logic for performance and type control.
- Like the Linux original, the generic helper functions expect callback operators defining ordering.
