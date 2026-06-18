# File Research: sources/os/bsd/freebsd-src/sys/sys/tree.h

Generic intrusive tree macro library for splay trees and rank-balanced trees.

Key responsibilities:
- Defines splay tree head/entry/access macros, initializers, rotations, link/assemble helpers, prototype generation, implementation generation, insert/remove/find/next/min/max wrappers, and iteration macros.
- Defines rank-balanced tree head/entry/access macros using low pointer bits in the parent pointer to encode red/rank-difference state.
- Implements weak-AVL-style rank-balanced insert, remove, rebalance, find, nearest-find, next/prev, adjacent-position insert, min/max, reinsert, and forward/reverse safe iteration macros.
- Supports static or external generated functions via `RB_PROTOTYPE[_STATIC]` and `RB_GENERATE[_STATIC]`.
- Provides augmentation hooks through `RB_AUGMENT`/`RB_AUGMENT_CHECK` and diagnostic rank verification when `_RB_DIAGNOSTIC` is enabled.

Dependencies:
- Includes `sys/cdefs.h`; assumes tree element pointers have at least two low zero bits for rank-balanced metadata.

Notable risks:
- This header generates real code through macros; comparator behavior, element alignment, and intrusive field use must be correct at every call site.
- Rank-balanced tree internals encode metadata in pointer bits, which is efficient but sensitive to unusual alignment or manual pointer manipulation.
- Augmentation hooks must be idempotent and correct, or tree metadata users can observe stale subtree summaries.
