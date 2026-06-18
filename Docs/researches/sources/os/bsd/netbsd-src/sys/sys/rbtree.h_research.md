# File Research: sources/os/bsd/netbsd-src/sys/sys/rbtree.h

Read completely: 223 lines.

This header declares NetBSD's intrusive red-black tree API. `rb_node_t` stores left/right child pointers plus parent, color, and side-position bits packed into `rb_info`; `rb_tree_t` stores the root, operation table, cached min/max pointers, and optional debug/statistics fields.

The public API includes tree initialization, insertion, lookup, lower/upper-bound lookup, removal, and iteration through `rb_tree_init`, `rb_tree_insert_node`, `rb_tree_find_node`, `rb_tree_find_node_geq`, `rb_tree_find_node_leq`, `rb_tree_remove_node`, and `rb_tree_iterate`. Convenience macros provide min/max, next/previous, and safe forward/reverse traversal.

Important interactions: callers embed `rb_node_t` at an offset described by `rb_tree_ops_t` and supply node/key comparison functions. Optional `RBDEBUG` adds a TAILQ list of nodes and tree checking; optional `RBSTATS` tracks operation counts.

Risks: the parent/color packing assumes node alignment leaves the low two pointer bits free. Comparison callbacks define tree ordering, so inconsistent callbacks can corrupt lookup/removal semantics.
