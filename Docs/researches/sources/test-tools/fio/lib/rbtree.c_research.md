# sources/test-tools/fio/lib/rbtree.c

Purpose: Linux-derived red-black tree balancing and traversal primitives for fio intrusive tree users.

Important APIs/functions: `rb_insert_color`, `rb_erase`, `rb_first`, and `rb_next`. Internal helpers rotate left/right and repair colors after deletion.

Control flow: callers perform ordinary BST insertion with `rb_link_node`, then call `rb_insert_color` to rebalance. Erase handles zero/one/two-child removal, swaps successor state when needed, and rebalances black-height violations. Traversal returns leftmost node and in-order successor.

State/persistence: mutates caller-embedded `fio_rb_node` parent/color and child pointers plus root. No allocation or locking.

Dependencies/integration: includes `rbtree.h`. Used by iolog verification history and other ordered fio structures.

Risks/test signals: callers own key comparison and duplicate handling; misuse can violate tree order even if colors are valid. Tests should insert/erase varied key sequences, verify in-order traversal, and validate color/black-height invariants.
