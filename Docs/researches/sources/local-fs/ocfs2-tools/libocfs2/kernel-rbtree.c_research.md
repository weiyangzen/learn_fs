# File Research: sources/local-fs/ocfs2-tools/libocfs2/kernel-rbtree.c

Provides a userspace copy of the Linux kernel red-black tree implementation.

Exported operations:
- `rb_insert_color()` rebalances and recolors after caller-linked insertion.
- `rb_erase()` removes a node and fixes tree coloring.
- `rb_first()` / `rb_last()` return minimum/maximum nodes.
- `rb_next()` / `rb_prev()` return in-order successor/predecessor.
- `rb_replace_node()` swaps a victim node with a replacement while preserving surrounding links and color.

Internal mechanics:
- `__rb_rotate_left()` and `__rb_rotate_right()` implement tree rotations.
- `__rb_erase_color()` handles delete fixup for black-height preservation.

Design notes:
- This file intentionally does not implement key comparison or insertion search; callers own embedding `struct rb_node` and deciding ordering.
- It is imported kernel infrastructure used where libocfs2 needs sorted in-memory structures.
- The implementation assumes valid rbtree state and non-null sibling nodes in delete fixup, matching kernel-style caller expectations.
