# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree_types.h

## Purpose
Minimal rbtree type definitions shared by rbtree headers and users.

## Contents
- `struct rb_node` with packed parent/color and left/right child pointers, aligned to `sizeof(long)`.
- `struct rb_root`.
- `struct rb_root_cached` with cached leftmost node.
- Initializers `RB_ROOT` and `RB_ROOT_CACHED`.
- C++ extern guard.

## Risks
No logic. ABI compatibility depends on keeping this layout aligned with rbtree implementation expectations.
