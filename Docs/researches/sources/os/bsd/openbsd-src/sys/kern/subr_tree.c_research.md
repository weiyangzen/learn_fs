# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_tree.c

Provides the generic runtime implementation behind OpenBSD red-black tree macros in `sys/tree.h`. It works on caller-owned objects using `struct rb_type` metadata: entry offset, comparison function, and optional augmentation callback.

Internal helpers translate between object pointers and embedded `struct rb_entry` pointers, access left/right/parent/color fields, initialize red entries, color parent/child nodes, and run optional augmentation after rotations or structural changes.

Insertion is implemented by `_rb_insert()`: descend by `t_compare`, reject duplicates by returning the existing node, link a new red entry under its parent, augment the parent if needed, and rebalance via `rbe_insert_color()` using standard red-black rotations and recoloring.

Removal is implemented by `_rb_remove()` and `rbe_remove()`: handle zero/one-child cases directly, replace two-child nodes with their inorder successor, repair parent/child links, run augmentation up the affected chain, and rebalance black-height via `rbe_remove_color()`.

Lookup and traversal APIs include `_rb_find()`, `_rb_nfind()` for first greater-or-equal match, `_rb_next()`, `_rb_prev()`, `_rb_root()`, `_rb_min()`, `_rb_max()`, and direct accessor/mutator helpers for left/right/parent links. `_rb_poison()` and `_rb_check()` support debugging of removed or uninitialized tree nodes.

The code assumes callers provide synchronization and valid comparison semantics. Optional augmentation is carefully called after rotations and parent changes so augmented interval or cached subtree metadata can remain consistent.

Filesystem relevance: generic kernel RB trees are used by many subsystems that need ordered lookup. In this group, `subr_pool.c` uses generated RB tree operations to map off-page pool page headers by page address.
