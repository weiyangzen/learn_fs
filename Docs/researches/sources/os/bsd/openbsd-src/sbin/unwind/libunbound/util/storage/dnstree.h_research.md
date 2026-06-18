# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.h

Defines DNS-name and address tree node types plus lookup APIs.

Key structures:
- `struct name_tree_node`: embedded `rbnode_type`, closest-encloser parent, wire-format name, length, label count, and DNS class.
- `struct addr_tree_node`: embedded `rbnode_type`, enclosing-netblock parent, `sockaddr_storage`, address length, and prefix length.

Public API:
- Name tree: `name_tree_init`, `name_tree_insert`, `name_tree_init_parents`, `name_tree_find`, `name_tree_lookup`, `name_tree_next_root`, `name_tree_compare`.
- Address tree: `addr_tree_init`, `addr_tree_addrport_init`, `addr_tree_insert`, `addr_tree_init_parents`, `addr_tree_init_parents_node`, `addr_tree_lookup`, `addr_tree_find`, `addr_tree_compare`, `addr_tree_addrport_compare`.

Usage contract:
- Nodes are caller allocated and typically embedded in larger records.
- Parent pointers must be initialized after insertions and before closest-encloser lookups.
- Tree objects are plain `rbtree_type` instances initialized with the appropriate comparator.
