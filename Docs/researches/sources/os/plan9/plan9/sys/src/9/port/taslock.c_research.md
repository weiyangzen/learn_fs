# File Research: sources/os/plan9/plan9/sys/src/9/port/taslock.c

Implements low-level spin locks, interrupt locks, and reference count atomics.

Spin locks:
- `lock` uses `tas` to acquire, increments `up->nlocks` to prevent scheduling, records holder PC/proc, and spins with diagnostics on long contention.
- `canlock` attempts nonblocking acquisition.
- `unlock` validates state, clears the lock, performs coherence, decrements `up->nlocks`, and calls `sched` if a delayed reschedule is pending at low interrupt level.

Interrupt locks:
- `ilock` raises priority with `splhi`, spins, records saved status register, holder PC/proc/Mach, and increments `m->ilockdepth`.
- `iunlock` validates interrupt-lock state, clears lock, decrements `ilockdepth`, clears `lastilock`, and restores priority with `splx`.

Reference helpers:
- `incref`/`decref` are implemented via static `inccnt`/`deccnt` around architecture atomics `_xinc`/`_xdec` in this file’s local helpers.
- `deccnt` panics if a reference count goes negative.

Diagnostics:
- Tracks lock statistics and optional lock-cycle maxima under `LOCKCYCLES`.
- `lockloop` prints lock holder and current process data on prolonged spin.
- Detects common misuse such as unlocking an `ilock` with `unlock`, `iunlock` while low, or unlocking from a different `up`.

Role:
- Foundational synchronization layer under all higher-level locks.
