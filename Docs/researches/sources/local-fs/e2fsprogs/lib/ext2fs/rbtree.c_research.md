# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.c

Linux-derived red-black tree implementation namespaced with `ext2fs_`. It implements rotations, insertion rebalancing, deletion rebalancing, erase, first/last traversal, next/previous traversal, and node replacement.

`ext2fs_rb_insert_color()` assumes callers already linked the new node in binary-search order with `ext2fs_rb_link_node()`. `ext2fs_rb_erase()` handles zero, one, and two-child deletion cases, using successor replacement for two-child nodes.

The implementation packs parent pointer and color in `rb_parent_color`, so node alignment and correct use of helper macros are essential. It provides no ordering callbacks; users must implement their own search/insert comparisons.
