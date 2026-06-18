# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/rbtree.h

This header ports the Linux red-black tree interface. It contains the original Linux rbtree usage comment, defines node/root structures, color and parent accessors, insertion-link helpers, and declares balancing/traversal routines implemented elsewhere.

Key definitions:
- `struct rb_node` stores `rb_parent_color`, `rb_right`, and `rb_left`, with parent pointer and color packed together.
- `struct rb_root` holds the tree root node.
- Defines `RB_RED`, `RB_BLACK`, `rb_parent`, `rb_color`, `rb_is_red`, `rb_is_black`, `rb_set_red`, `rb_set_black`, `rb_set_parent`, and `rb_set_color`.
- Defines `RB_ROOT`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, and `RB_CLEAR_NODE`.
- Declares `rb_insert_color`, `rb_erase`, `rb_next`, `rb_prev`, `rb_first`, `rb_last`, `rb_replace_node`, and a generic `rb_insert`.
- Inline `rb_link_node` initializes a newly linked node and stores it into the parent’s child pointer.

Dependencies:
- Uses `ULONG_PTR`, `container_of`, and `__attribute__`, which are provided by the local compatibility headers.
- Runtime behavior depends on `src/rbtree.c`, not part of this group.

Research notes:
- The tree is used by the ext2 compatibility/block layer for structures such as buffer-head lookup trees.
- `RB_CLEAR_NODE(node)` sets the parent pointer to the node itself. In this header, `RB_EMPTY_NODE(node)` is defined as `rb_parent(node) != node`; this is inverted from the common Linux idiom and means cleared nodes test false under this macro. Callers need to match this local semantic or avoid relying on it.
