# File Research: sources/local-fs/dlm/dlm_controld/rbtree_types.h

This header defines the rb-tree storage types copied from Linux.

It provides:
- `struct rb_node` with packed parent/color field and left/right child pointers.
- `struct rb_root`.
- `struct rb_root_cached` with an O(1) leftmost pointer.
- Initializers `RB_ROOT` and `RB_ROOT_CACHED`.

Used by:
- `rbtree.h`, `rbtree_augmented.h`, `rbtree.c`, and `plock.c`.

Notable detail:
- `struct rb_node` is aligned to `sizeof(long)`, matching the Linux implementation’s assumptions for storing color bits in low pointer bits.
