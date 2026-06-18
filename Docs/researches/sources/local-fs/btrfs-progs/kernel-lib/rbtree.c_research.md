# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree.c

## Purpose
Userspace adaptation of Linux red-black tree insertion, deletion, replacement, and iteration.

## Key Interfaces Implemented
- Rebalancing: `rb_insert_color`, `rb_erase`, `__rb_insert_augmented`, `__rb_erase_color`.
- Ordered traversal: `rb_first`, `rb_last`, `rb_next`, `rb_prev`.
- Replacement: `rb_replace_node`.
- Postorder traversal: `rb_first_postorder`, `rb_next_postorder`.

## Dependencies
Includes `kerncompat.h`, rbtree type/header files, and augmented rbtree declarations.

## Notable Behaviors
- Parent pointer and color are packed in `__rb_parent_color`.
- Rotations use `WRITE_ONCE()` for child pointers to support lockless lookup constraints described in comments.
- Non-augmented operations use dummy augment callbacks so common augmented erase/insert code can be reused.
- Deletion handles standard red-black erase cases and returns a rebalance parent for augmented callers.

## Risks
- The API provides tree mechanics only; caller code must implement ordering and search correctly.
- Lockless traversal comments guarantee termination and valid elements, not a consistent snapshot.
- Misuse of `rb_replace_node()` with an already-linked replacement node would corrupt tree structure.
