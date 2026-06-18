# sources/user-network-fs/nfs-ganesha/src/test/test_avl.c

Purpose: CUnit regression test for the project AVL tree implementation, covering insertion, lookup, traversal, deletion, minimum, supremum, and infimum behavior at several sizes.

Important APIs, types, and functions: defines `avl_unit_val_t` with `node_k`, key, and value. Uses `avltree_init`, `avltree_insert`, `avltree_lookup`, `avltree_remove`, `avltree_first`, `avltree_next`, `avltree_sup`, `avltree_inf`, and `avltree_size`. CUnit suites register tests for 1, 2, 100, 10000, random 100000 min, and supremum cases.

Control flow: each suite initializes a global tree, tests insert deterministic values, validate some lookups/traversals, delete values, and cleanup. Later tests rebuild `avl_tree_1` for delete/min scenarios and use random inserts to check tracked minimum.

State and persistence: global AVL trees store heap-allocated test nodes for each suite. Cleanup frees nodes in most cases.

Dependencies and integration points: links against `ganesha_nfsd`, `abstract_mem`, `avltree`, and CUnit via the test CMake file.

Risks: `avl_unit_clear_tree` removes nodes from `avl_tree_1` regardless of the tree argument, so it is only safe for the paths that actually use tree 1. Many "check" functions assert only `0 == 0`, so structural invariants are not deeply verified. Lookup paths dereference returned nodes without asserting non-NULL first. Random min uses `srand(time(0))`, making failures less reproducible.

Test signals: if run, it catches basic ordering/traversal/delete regressions, but it is weak for balancing invariants, duplicate insertion handling, and memory correctness.
