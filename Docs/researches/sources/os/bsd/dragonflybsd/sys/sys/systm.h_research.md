# File Research: sources/os/bsd/dragonflybsd/sys/sys/systm.h

Central kernel system declarations and utility API surface.

Key responsibilities:
- Exposes boot/runtime globals:
  - `securelevel`, `cold`, `panicstr`, `dumping`, `boothowto`, `bootverbose`, `ncpus`, `physmem`, root/dump devices, release/version data
- Defines assertion macros:
  - `KASSERT`
  - `KKASSERT`
  - `KKASSERT_UNSPIN`
  - `__assert_unreachable`
- Defines data placement/cacheline annotations.
- Declares initialization, CPU, VM, trap, TLS, CRC, logging/printing, scanning, string conversion, memory, copyin/out, user-access, delay, profiling, environment, startup/shutdown, clock, sleep/wakeup, device number, unit-number, and bit-count helpers.
- Maps common memory functions to compiler builtins while preserving underscore-prefixed real implementations.

Important behavior:
- Kernel-only header; userland inclusion errors out.
- Builtin memory macros use `__DEQUALIFY` and can affect compiler assumptions.
- `copyin/copyout` and `fuword/suword/casu/swapu` declarations define user-kernel memory access primitives.
- Sleep APIs cover bare channels and variants tied to spinlocks, lockmgr locks, mutexes, and serializers.
- Wakeup APIs include per-CPU, domain, one-shot, and delayed wakeup variants.
- `muldivu64` uses a 128-bit intermediate and emits diagnostics on overflow.

Research notes:
- This is a broad dependency hub used to avoid including heavier subsystem headers everywhere.
- The header mixes stable kernel contracts with low-level machine hooks.
