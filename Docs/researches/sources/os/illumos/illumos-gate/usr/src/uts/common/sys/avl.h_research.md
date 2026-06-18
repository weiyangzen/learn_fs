# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl.h

This header defines the public generic AVL tree API used in illumos. It describes the intrusive-node model, comparator contract, tree lifecycle, lookup/insertion/removal, traversal, update, swap, and teardown helpers.

Key contents:
- Comparator helpers `AVL_ISIGN`, `AVL_CMP`, and `AVL_PCMP`.
- Opaque/public typedefs `avl_tree_t`, `avl_node_t`, and `avl_index_t`.
- Direction constants `AVL_BEFORE` and `AVL_AFTER`.
- API prototypes:
  - `avl_create`, `avl_find`, `avl_insert`, `avl_insert_here`
  - `avl_first`, `avl_last`, `avl_nearest`
  - `avl_add`, `avl_remove`
  - `avl_update`, `avl_update_lt`, `avl_update_gt`
  - `avl_swap`, `avl_numnodes`, `avl_is_empty`
  - `avl_destroy_nodes`, `avl_destroy`
- Traversal macros `AVL_NEXT` and `AVL_PREV`.

Dependencies:
- Includes `sys/types.h` and private implementation header `sys/avl_impl.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The data structure is intrusive: caller-owned structs embed `avl_node_t`.
- Thread safety is explicitly caller-managed.
- Comparator must return exactly `-1`, `0`, or `+1`.
