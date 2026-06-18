# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.h

Defines the intrusive red-black tree interface.

Key structures:
- `rbnode_type`: parent/left/right links, `key`, and color byte. Must be the first member of user objects.
- `rbtree_type`: root pointer, node count, and comparison callback.
- `RBTREE_NULL`: global sentinel node, not a C null pointer.

Public operations:
- Create/init: `rbtree_create`, `rbtree_init`.
- Mutation: `rbtree_insert`, `rbtree_delete`.
- Lookup: `rbtree_search`, `rbtree_find_less_equal`.
- Traversal: `rbtree_first`, `rbtree_last`, `rbtree_next`, `rbtree_previous`, `RBTREE_FOR`, `traverse_postorder`.

Usage contract:
- Callers allocate and free contained objects.
- Duplicate keys are rejected on insert.
- `traverse_postorder` callback must not remove nodes because rebalancing would invalidate traversal assumptions.
