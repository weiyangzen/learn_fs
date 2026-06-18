# File Research: sources/os/bsd/dragonflybsd/sys/sys/spinlock.h

This header defines the basic DragonFly spinlock structure and shared/exclusive bit layout.

Key responsibilities:
- Defines `struct spinlock`:
  - `lock` count/flags word
  - `update` counter
- Defines `SPINLOCK_INITIALIZER`.
- Defines spinlock bit constants:
  - `SPINLOCK_SHARED`
  - `SPINLOCK_EXCLWAIT`
  - `SPINLOCK_EXCLWAIT_MASK`
  - `SPINLOCK_EXCLWAIT_SHIFT`

Important invariants:
- The structure is retained for both SMP and UP builds, preserving embedded-structure size.
- DragonFly spinlocks use a count/flag system.
- Shared spinlocks are supported.
- There is no description field; wait descriptions are pulled from `__func__` in acquisition wrappers.

Research notes:
- This is the structural/bit-definition half of spinlocks; inline behavior is in `spinlock2.h`.
