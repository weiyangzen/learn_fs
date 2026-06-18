# File Research: sources/teaching/os161/kern/include/spinlock.h

Defines the machine-independent public interface for OS/161 spinlocks. `struct spinlock` wraps the machine-dependent lock word, the owning CPU pointer, and optional Hangman deadlock-detector metadata. The header emphasizes that spinlocks are CPU-owned, not thread-owned, and that users should treat the structure as opaque despite its public layout for static allocation.

Exports `SPINLOCK_INITIALIZER`, `spinlock_init`, `spinlock_cleanup`, `spinlock_acquire`, `spinlock_release`, and `spinlock_do_i_hold`. Acquisition disables interrupts and release may restore them, making this file tightly coupled to `spl.h`, `machine/spinlock.h`, current CPU state, and low-level scheduler invariants.

Risk points: callers must not inspect internals directly, cleanup requires the lock to be unlocked, and misuse can block interrupts or deadlock CPUs.
