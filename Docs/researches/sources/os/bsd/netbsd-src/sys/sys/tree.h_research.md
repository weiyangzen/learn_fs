# File Research: sources/os/bsd/netbsd-src/sys/sys/tree.h

Read completely: 761 lines.

Defines macro-generated splay tree and red-black tree containers.

Key elements:
- Provides `SPLAY_HEAD`, `SPLAY_ENTRY`, initializer/accessor macros, rotations, generated prototypes, and generated implementations for insert, remove, find, next, min, max, and traversal.
- Splay operations move searched keys near the root and mutate tree shape on lookup.
- Provides `RB_HEAD`, `RB_ENTRY`, initializer/accessor macros, color/parent helpers, rotations, and `RB_AUGMENT` hook.
- Red-black generation supports normal and static prototypes/implementations.
- Red-black operations include insert with recoloring, remove with fixup, find, nearest find, next/previous, min/max, and forward/reverse safe traversal macros.

Risks and notes:
- Type safety is macro-based; caller-provided compare functions and embedded fields must be correct.
- Splay lookup writes to the tree, which matters for locking and read-only assumptions.
- `RB_AUGMENT` must be correct if clients maintain augmented metadata.
