# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_spinlock.c

## Purpose

`kern_spinlock.c` implements the contended slow paths for DragonFlyBSD exclusive/shared spinlocks, including exclusive-wait priority, shared-lock admission windows, indefinite-wait diagnostics, sysctl tuning, and invariant-only lock tests.

## Main Contents

- Global state:
  - Defines `pmap_spin`.
  - Exposes `debug.spin_backoff_max`, `debug.spin_window_shift`, and `debug.indefinite_uses_rdtsc`.
  - Under debug/invariants, exposes latency injection and `debug.spin_lock_test`.
- Exclusive contention:
  - `spin_trylock_contested()` handles the degenerate shared-flag case for trylock, otherwise unwinds the optimistic inline attempt by decrementing spinlock accounting and leaving the critical section.
  - `_spin_lock_contested()` receives an already-incremented lock word from the inline fast path, converts the attempt into a high-bit exclusive wait reservation, clears `SPINLOCK_SHARED`, waits for low bits to drain, then atomically transfers the reservation into an exclusive hold.
  - The wait loop uses an increasing backoff, optional TSC CPU-windowing, and `indefinite_check()` diagnostics.
- Shared contention:
  - `_spin_lock_shared_contested()` undoes the inline increment, then loops until it can set `SPINLOCK_SHARED|1`, increment an already shared lock, or selectively bypass exclusive-wait priority during its TSC admission window.
  - Shared locks avoid exponential backoff for performance and rely on exclusive priority/windowing to avoid starving either side.
- Initialization and tests:
  - `spinlock_sysinit()` disables RDTSC-based indefinite behavior under virtual-machine guests.
  - `sysctl_spin_lock_test()` can force indefinite wait behavior or time best-case exclusive lock overhead when `INVARIANTS` is enabled.

## State And Dependencies

The lock word packs low-bit holders/shared flag and high-bit exclusive waiters. The code depends on machine atomics, CPU pause/fence/rdtsc helpers, critical-section accounting, per-CPU spinlock counts, KTR, and the indefinite-wait framework.

## Risks And Invariants

The slow paths assume the inline fast paths have already adjusted critical-section and spinlock state. Exclusive acquisition must preserve earlier exclusive waiters and clear stale shared state. Shared acquisition must balance two starvation risks: always respecting exclusive waiters can starve readers, while always ignoring them can starve writers.
