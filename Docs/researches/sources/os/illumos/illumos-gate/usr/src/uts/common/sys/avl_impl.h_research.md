# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avl_impl.h

This private header defines the concrete AVL node/tree layout and low-level macros used by `avl.h` and the AVL implementation. It warns applications not to include it directly.

Key contents:
- `struct avl_node` layout differs by pointer width:
  - 32-bit: children, parent pointer, child index, and balance as separate fields.
  - 64-bit: two child pointers plus packed `avl_pcb` containing parent pointer, child index, and balance in low bits.
- Accessor macros for parent, child index, and balance:
  - `AVL_XPARENT`, `AVL_SETPARENT`
  - `AVL_XCHILD`, `AVL_SETCHILD`
  - `AVL_XBALANCE`, `AVL_SETBALANCE`
- Node/data conversion macros `AVL_NODE2DATA` and `AVL_DATA2NODE`.
- `avl_index_t` packing/extraction macros.
- `struct avl_tree` layout: root, comparator, node offset, node count, user struct size.
- Internal traversal function `avl_walk`.

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The 64-bit layout assumes pointer alignment leaves the low three bits available.
- Tree fields are ordered for `avl_find()` cache-line locality.
