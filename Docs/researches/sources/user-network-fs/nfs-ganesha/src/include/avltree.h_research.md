<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/avltree.h -->
# sources/user-network-fs/nfs-ganesha/src/include/avltree.h

## Purpose
`avltree.h` is a vendored libtree header that declares intrusive binary-search tree, red-black tree, AVL tree, and splay tree APIs. NFS-Ganesha heavily uses the AVL portion for caches and indexes.

## Important APIs, types, and functions
- `*_container_of` macros recover parent objects from embedded tree nodes.
- BST declarations include `struct bstree_node`, `struct bstree`, comparator type, first/last/next/prev, lookup, insert, remove, replace, and init.
- Red-black declarations mirror that API with `struct rbtree_node`, `enum rb_color`, and `struct rbtree`.
- AVL declarations include packed/aligned `struct avltree_node`, `get_balance()`, `avltree_cmp_fn_t`, `struct avltree`, inline lookup/insert helpers, first/last accessors, next/prev, size, inf/sup, remove, replace, and init.
- Splay declarations include analogous node/tree and operation prototypes.

## Control flow
Intrusive tree users embed a node in their object and provide a comparator that maps nodes back to containing objects. `avltree_insert()` performs a lookup; if a duplicate is found, it returns the existing node, otherwise it calls `avltree_do_insert()` to rebalance and update metadata. Lookup follows comparator results down the tree. Iteration starts at cached first/last pointers and uses next/prev helpers.

## State and persistence
Tree state is stored in caller-owned `struct *tree` and embedded node fields. The AVL tree tracks root, comparator, height, first/last nodes, and size. There is no persistence beyond the in-memory indexes maintained by callers.

## Dependencies and integration points
It depends on integer and offset types and is implemented by companion source files in the tree library. It is integrated across Ganesha for idmapper caches, client maps, filesystem indexes, and other ordered intrusive collections.

## Risks
- Intrusive nodes can belong to only one tree at a time unless the containing object has multiple node members.
- Comparators must define a strict weak ordering and match the node member used for container lookup; mistakes corrupt tree behavior.
- The packed parent/balance representation depends on pointer alignment and `UINTPTR_MAX`; portability needs coverage.
- Tree operations are not internally synchronized. Callers must provide locks.
- Duplicate insert returns the existing node and does not replace automatically; callers must explicitly handle replacement.

## Test signals
- Tree tests should cover insert, duplicate insert, lookup, remove, replace, first/last, next/prev, inf/sup, and size.
- Stress tests should insert/remove random keys while validating sorted traversal and AVL balance.
- Portability builds should cover 32-bit and 64-bit targets and compilers with/without GNU extensions.
- Caller-specific tests should validate comparators for each embedded-node use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/avltree.h -->
