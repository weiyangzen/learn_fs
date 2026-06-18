# sources/user-network-fs/nfs-ganesha/src/avl/rb.c

Purpose: Implements an intrusive red-black tree with parent pointers, cached first/last nodes, and optional parent/color bit packing.

Important APIs/types/functions: Exports `rbtree_first()`, `rbtree_last()`, `rbtree_next()`, `rbtree_prev()`, `rbtree_lookup()`, `rbtree_insert()`, `rbtree_remove()`, `rbtree_replace()`, and `rbtree_init()`. Internal helpers manage color/parent access, rotations, lookup, and child assignment.

Control flow: Insert performs normal BST insertion, colors the new node red, updates endpoint caches, then repairs red-black properties with recoloring and at most two rotations before forcing the root black. Removal selects successor if needed, transplants nodes, preserves successor color, handles easy red/single-red-child cases, and otherwise performs the standard double-black fixup with sibling recoloring/rotation. Iterators use parent links and subtree extremes.

State and persistence behavior: In-memory intrusive state only. Color may be stored in the low bit of the parent word, so alignment is part of the data representation.

Dependencies and integration points: Uses `avltree.h` shared declarations. Consumers supply stable comparators and node storage.

Risks: Delete fixup assumes sibling pointers exist in cases where red-black invariants require them; corrupted trees can crash. Replacement copies node memory and must be used only when callers manage embedded container implications. There is no explicit size field, unlike AVL. Packed parent/color mode can fail on unusual pointer representations.

Test signals: Randomized insert/delete with red-black invariant validation, endpoint iteration checks, root removal, replacement, duplicate insertion, and builds on platforms with and without `UINTPTR_MAX`.
