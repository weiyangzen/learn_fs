# sources/user-network-fs/nfs-ganesha/src/avl/bst.c

Purpose: Implements an intrusive threaded binary search tree with cached first/last nodes and optional thread-bit packing in pointer low bits.

Important APIs/types/functions: Exports `bstree_first()`, `bstree_last()`, `bstree_next()`, `bstree_prev()`, `bstree_lookup()`, `bstree_insert()`, `bstree_remove()`, `bstree_replace()`, and `bstree_init()`. Internal helpers distinguish child links from predecessor/successor threads.

Control flow: `do_lookup()` walks by comparator and returns matching node or insertion parent/side. Insert initializes the node and attaches it with predecessor/successor threads. Iteration follows real child links to subtree extremes or thread links. Removal handles leaf, one-child, and two-child cases, updating threads and cached endpoints. Replace finds the parent when needed, rewires parent/root and adjacent thread references, then copies the old node into the new node.

State and persistence behavior: Intrusive in-memory tree only; no allocation or persistence. Thread markers are either explicit booleans or low-bit pointer tags depending on platform support.

Dependencies and integration points: Includes `avltree.h` for shared tree declarations. Consumers own node storage and comparator behavior.

Risks: The tree is unbalanced, so ordered insertions can degrade to linear lookup/remove. Low-bit tagging requires pointer alignment. Removal calls `do_lookup(node, tree, ...)` and assumes comparator identity locates the actual node. Thread updates are easy to break around first/last and two-child removal.

Test signals: Verify inorder iteration after each insert/remove, first/last changes, removal of root/leaf/one-child/two-child nodes, replacement preserving threads, duplicate insert return, and pathological sorted insertion performance expectations.
