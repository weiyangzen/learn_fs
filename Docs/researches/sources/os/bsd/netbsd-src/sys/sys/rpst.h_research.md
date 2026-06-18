# File Research: sources/os/bsd/netbsd-src/sys/sys/rpst.h

Read completely: 67 lines.

This header declares a priority search tree structure. `struct rpst_tree` holds root and height, `struct rpst_node` stores parent, two children, and `x/y` keys, and `struct rpst_iterator` stores range-iteration state.

APIs include tree initialization, insert, remove, first matching node, and next matching node: `rpst_init_tree`, `rpst_insert_node`, `rpst_remove_node`, `rpst_iterate_first`, and `rpst_iterate_next`.

Risks: callers manage node storage and key values directly. Correct range iteration depends on tree invariants maintained by the implementation.
