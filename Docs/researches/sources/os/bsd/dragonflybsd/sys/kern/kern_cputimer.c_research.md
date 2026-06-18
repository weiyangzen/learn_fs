# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_cputimer.c

## Purpose

Provides DragonFlyBSD’s generic CPU timer, interrupt timer, and CPU counter registration/selection infrastructure. It abstracts free-running counters used by systimers and per-CPU timer interrupts.

## Key Responsibilities

- Maintains the selected `sys_cputimer`, starting with a monotonic dummy timer.
- Registers and deregisters candidate `struct cputimer` implementations.
- Computes frequency conversion helpers for microseconds/nanoseconds.
- Registers, selects, configures, restarts, and power-save-switches interrupt cputimers.
- Dispatches per-CPU timer interrupts into `systimer_intr()`.
- Registers and selects `struct cpucounter` implementations for MP-safe or per-CPU counter use.
- Exposes timer state through `kern.cputimer.*` sysctls.

## Main Entry Points

- `cputimer_select()` switches the active timer if priority allows, preserving continuity by constructing the new timer from the old count and warning if it jumps backward.
- `cputimer_register()` / `cputimer_deregister()` maintain the timer list and fall back to the dummy timer when needed.
- `cputimer_set_frequency()`, `cputimer_default_fromhz()`, `cputimer_default_fromus()` handle tick conversion.
- `cputimer_intr_register()`, `cputimer_intr_deregister()`, `cputimer_intr_select()` maintain interrupt timer providers.
- `cputimer_intr_select_caps()` selects the best interrupt timer matching required capability bits.
- `cputimer_intr_powersave_addreq()` / `cputimer_intr_powersave_remreq()` switch interrupt timer capabilities around power-saving requirements.
- `pcpu_timer_process()` and `pcpu_timer_process_frame()` process per-CPU timer events.
- `cpucounter_find_pcpu()`, `cpucounter_find()`, `cpucounter_register()` manage CPU counter backends.

## Important State

- `dummy_cputimer` and `dummy_cpucounter` provide always-available fallbacks.
- `sys_cputimer` points at the active free-running counter.
- `cputimerhead` stores registered cputimers.
- `sys_cputimer_intr`, `cputimer_intr_caps`, and `cputimer_intr_head` track selected and available interrupt timers.
- `cputimer_intr_ps_reqs` counts active power-save requests, protected by `cputimer_intr_ps_slize`.
- `cpucounterhead` stores registered CPU counters.

## Control Flow

- Timer selection updates conversion fields, calls the new timer’s `construct()`, reconfigures interrupt timers, updates `sys_cputimer`, destructs the old timer, and notifies `systimer_changed()`.
- Interrupt cputimer initialization is deferred via `SYSINIT(cputimer_intr, SI_BOOT2_CLOCKREG, SI_ORDER_SECOND, ...)`.
- Per-CPU timer interrupt handling calls optional provider-specific `pcpuhand`, clears `gd_timer_running`, then dispatches pending `gd_systimerq` work.
- Power-save add/remove paths reselect interrupt timers by capability and restart the timer if selection changed.

## Sysctl Surface

- `kern.cputimer.select`, `name`, `clock`, `freq`.
- `kern.cputimer.intr.reglist`, `freq`, `select`.

## Filesystem/Storage Relevance

Not filesystem-specific, but storage and VFS subsystems depend on kernel timers for timeouts, delayed work, buffer scheduling, and periodic cleanup. Timer monotonicity and interrupt-timer reliability matter for I/O scheduling correctness.

## Research Notes

- `cpucounter_find()` requires `CPUCOUNTER_FLAG_MPSYNC` and asserts that the selected counter is MP-safe.
- Power-save switching uses `ERESTART` internally to signal that the interrupt timer changed and must be restarted.
- The dummy counter uses `microuptime()` and is lower priority than hardware backends.
