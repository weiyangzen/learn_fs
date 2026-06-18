# File Research: sources/local-fs/gfs2-utils/gfs2/include/osi_tree.h

This header implements an intrusive red-black tree adapted from Linux kernel rbtree code. It is used for ordered fsck/libgfs2 structures such as directory trees, duplicate-block trees, and resource-group trees.

It defines:
- `struct osi_node` with parent/color packed into `osi_parent_color`.
- `struct osi_root`.
- Color/parent accessors and mutators.
- `osi_link_node()` for attaching a new node before rebalancing.
- Insert rebalancing via `osi_insert_color()`.
- Erase rebalancing via `osi_erase()` and `__osi_erase_color()`.
- Ordered traversal helpers `osi_first()`, `osi_last()`, `osi_next()`, `osi_prev()`.
- `osi_replace_node()`.

The implementation is entirely inline in the header. Callers are responsible for key comparisons and embedding `struct osi_node` in their own container types.

Risks and notes:
- The tree API assumes caller-managed ordering and node lifetime.
- `__osi_erase_color()` expects sibling pointers in typical rbtree erase cases; corrupt tree state would crash.
- Parent/color bit packing assumes pointer alignment leaves low bits available.
