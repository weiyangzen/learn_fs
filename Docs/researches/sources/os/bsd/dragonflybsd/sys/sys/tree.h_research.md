# File Research: sources/os/bsd/dragonflybsd/sys/sys/tree.h

## Summary
Generic intrusive splay-tree and red-black-tree macro framework used throughout DragonFly BSD kernel and user-visible code.

## Main Responsibilities
- Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, generated prototypes, generated insert/remove/find/next/min/max routines, and traversal macros.
- Defines `RB_HEAD`, `RB_ENTRY`, generated red-black insert/remove/find/scan/next/prev/min/max routines, and traversal macros.
- Adds DragonFly-specific red-black scan tracking through `rbh_inprog` so scanned nodes can be deleted while a scan is active.
- Provides extended red-black lookup generators for exact numeric keys, relative numeric lookups, ranged lookups, and custom comparator lookups.

## Important Behavior
Splay operations move accessed nodes toward the root and mutate the tree on lookup. Red-black operations preserve parent/color metadata and support optional `RB_AUGMENT()` hooks during rotations and parent updates. Kernel builds use `rb_spin_lock()`/`rb_spin_unlock()` around scan-info manipulation; non-kernel builds compile scan locking away.

## Risks
This is macro-generated container code with intrusive node fields, so comparator consistency, field names, and duplicate-key handling are entirely caller-controlled. `RB_INIT()` clears root and in-progress scan state but does not initialize the embedded spinlock, so callers must use a valid initialization pattern for kernel scan locking.
