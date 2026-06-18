# File Research: sources/os/bsd/dragonflybsd/sys/sys/systimer.h

Kernel system timer, CPU timer, interrupt timer, and CPU counter interfaces.

Key contents:
- Defines `sysclock_t` and `ssysclock_t`.
- Defines `struct systimer` for per-CPU queued/nonqueued timers:
  - queue linkage
  - absolute next time
  - periodic interval/frequency
  - callback
  - flags
  - owning timer and CPU globaldata
- Defines `SYSTF_*` flags for queue state, IPI running, nonqueued timers, synchronization offsets, and coincident ordering.
- Declares systimer operations for add/delete/init/adjust/intr.
- Defines `struct cputimer` for monotonic free-running counters.
- Defines CPU timer type and priority constants.
- Defines `struct cputimer_intr` for one-shot interrupt timers.
- Defines interrupt timer priorities/capabilities and register/select helpers.
- Defines `struct cpucounter` and lookup/register APIs.

Important invariants:
- `cputimer->count()` must be MP synchronized, stable through power-saving, and monotonically increasing.
- `count()` returns a full-width wrapping counter.
- Frequency conversion uses precomputed 64-bit factors and `muldivu64`.
- Interrupt timer implementations expose `reload`, `enable`, `config`, `restart`, `pmfixup`, `initclock`, and optional per-CPU handler hooks.
- `cputimer_intr_deregister()` cannot remove the currently selected interrupt timer.

Research notes:
- This header separates timebase selection from interrupt delivery.
- It documents hardware/platform requirements more explicitly than most kernel headers.
