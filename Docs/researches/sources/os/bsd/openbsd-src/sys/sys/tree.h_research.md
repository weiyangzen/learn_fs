# File Research: sources/os/bsd/openbsd-src/sys/sys/tree.h

Defines generic intrusive tree APIs: macro-generated splay trees, macro-generated red-black trees, and a newer runtime-described red-black tree wrapper family. The splay API provides heads, entries, rotations, insertion, removal, find, next, min/max, and foreach traversal.

The classic `RB_*` macros generate type-specialized red-black insert/remove/find/near-find/next/prev/min/max functions with optional `RB_AUGMENT`. The later `RBT_*` API uses `struct rb_type`, `struct rb_tree`, and `struct rb_entry` plus helper functions such as `_rb_insert`, `_rb_remove`, `_rb_find`, and poisoning/checking helpers. This file underpins many kernel indexed containers, including vnode buffer and namecache trees.
