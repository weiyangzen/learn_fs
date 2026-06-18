# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/rbtree.c

This is a Linux red-black tree implementation ported into the ReactOS Ext2 source tree.

It provides rotation helpers, insertion rebalancing, erase rebalancing, ordered traversal (`rb_first`, `rb_last`, `rb_next`, `rb_prev`), replacement, and a convenience `rb_insert` that accepts a caller-provided comparator.

The tree stores parent and color through the Linux `rb_parent_color` convention and exports the main functions with `EXPORT_SYMBOL`.

`rb_insert` ignores duplicate keys by returning without inserting when the comparator returns zero. No memory allocation, key ownership, or synchronization is handled here.

Research notes: correctness depends on callers maintaining valid `rb_node` links and external locking. Erase balancing follows the classic Linux algorithm and assumes tree invariants; corrupted trees can lead to null sibling dereferences.
