# sources/user-network-fs/nfs-ganesha/src/avl/avl.c

Purpose: Implements an intrusive AVL tree with parent pointers, cached first/last nodes, size/height accounting, and optional parent/balance bit packing on 64-bit pointer platforms.

Important APIs/types/functions: Exports `avltree_next()`, `avltree_prev()`, `avltree_size()`, `avltree_inf()`, `avltree_sup()`, `avltree_do_insert()`, `avltree_remove()`, `avltree_replace()`, and `avltree_init()`. Internal helpers manage parent/balance access, first/last traversal, `rotate_left()`, `rotate_right()`, and child assignment.

Control flow: Lookup-like infimum/supremum walks use the user comparator. Insertion initializes the node, links it under the located parent, updates cached first/last, walks back to the nearest unbalanced ancestor updating balances, then applies single or double rotations. Removal chooses a successor, relinks children/parent, updates first/last and size, then walks upward applying AVL delete rebalancing until height stabilizes. Replace rewires parent/child caches and copies the old node payload into the replacement.

State and persistence behavior: Tree state lives entirely in caller-provided `struct avltree` and embedded nodes. It stores no allocations and performs no persistence. On suitable platforms, low parent pointer bits encode balance, so node alignment is an implicit state invariant.

Dependencies and integration points: Uses `avltree.h` for node/tree layouts and comparator types. Consumers must embed `avltree_node` in their own objects and provide a strict comparator.

Risks: Intrusive replacement copies the whole node struct and requires callers to ensure the replacement's container state remains valid. Packed parent/balance mode depends on pointer alignment and `UINTPTR_MAX == UINT64_MAX`. Comparator instability or duplicate handling mistakes can corrupt tree ordering. `avltree_replace()` has a comment expressing skepticism about replacing a non-tree/rootless node and increments size in that branch.

Test signals: Insert ascending/descending/random keys, duplicate insert path through higher-level caller, delete leaf/one-child/two-child/root nodes, first/last maintenance, inf/sup edge cases, replace root and non-root, 32-bit fallback layout, and invariant checks for height/balance after randomized operations.
