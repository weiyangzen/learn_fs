# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_rbtree.c

## Summary
Tiny support file for generic red-black tree scanning synchronization.

## Main Responsibilities
- Provides `rb_spin_lock()` and `rb_spin_unlock()` wrappers around DragonFly spin locks.
- Supports `RB_SCAN` helper linkage when tree scans occur under shared locks.

## Important Behavior
The comment describes use with shared VM object locks, where temporary scan-info linkage needs its own spinlock.

## Risks
Correctness depends on higher-level RB tree users supplying and using the spinlock consistently around scan linkage.
