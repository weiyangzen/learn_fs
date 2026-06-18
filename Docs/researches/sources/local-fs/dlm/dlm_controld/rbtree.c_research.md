# File Research: sources/local-fs/dlm/dlm_controld/rbtree.c

This is a userspace copy of Linux `lib/rbtree.c`. It implements red-black tree insertion, deletion/rebalancing, replacement, and traversal.

Provided functions:
- `rb_insert_color()`
- `rb_erase()`
- `__rb_insert_augmented()`
- `__rb_erase_color()`
- `rb_first()`, `rb_last()`
- `rb_next()`, `rb_prev()`
- `rb_replace_node()`
- `rb_first_postorder()`, `rb_next_postorder()`

Implementation characteristics:
- Parent pointer and color are stored together in `__rb_parent_color`.
- Rotations use `WRITE_ONCE()` for child pointer updates.
- Non-augmented erase/insert use dummy callbacks so augmented logic is optimized out.
- Augmented operation support delegates propagation/copy/rotate work through callbacks declared in `rbtree_augmented.h`.

Used by:
- `plock.c`, which stores plock resources in `ls->plock_resources_root` keyed by resource number.

Notable details:
- Comments include Linux’s lockless lookup caveats: traversals may miss subtrees during concurrent rotations, but should not loop or return invalid elements if pointer stores obey the constraints.
- In `dlm_controld`, tree use appears single-threaded/serialized by daemon state locks rather than relying on lockless lookup semantics.
