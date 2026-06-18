# File Research: sources/local-fs/dlm/dlm_controld/rbtree_augmented.h

This is a userspace copy of Linux `include/linux/rbtree_augmented.h`. It supports rb-trees with per-subtree augmented metadata.

Key contents:
- `struct rb_augment_callbacks` with `propagate`, `copy`, and `rotate` callbacks.
- `rb_insert_augmented()` and `rb_insert_augmented_cached()`.
- Macro templates `RB_DECLARE_CALLBACKS` and `RB_DECLARE_CALLBACKS_MAX`.
- Color and parent helpers: `RB_RED`, `RB_BLACK`, `rb_color`, `rb_is_red`, `rb_is_black`, `rb_set_parent`, `rb_set_parent_color`.
- `__rb_change_child()` and `__rb_erase_augmented()`.
- `rb_erase_augmented()` and cached variant.

Used by:
- `rbtree.c`, which includes this header for both augmented and non-augmented erase/insert internals.

Notable details:
- The comments explicitly say most of the header is implementation detail; public consumers should generally depend only on callbacks and augmented insert/erase APIs.
- The current plock resource tree does not use augmented metadata, but the full support is present.
