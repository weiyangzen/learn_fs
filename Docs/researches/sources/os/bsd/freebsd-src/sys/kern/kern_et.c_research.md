# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_et.c

Read completely: 263 lines.

## Purpose
Implements the generic event timer registry and control helpers used by platform timer drivers and CPU timer-selection code.

## Main Elements
- Maintains a global quality-sorted SLIST of registered `struct eventtimer` instances protected by `et_eventtimers_mtx`.
- `et_register()` validates timer start support, prints timer quality/frequency, creates per-timer sysctl nodes, and inserts by descending quality.
- `et_deregister()` invokes an optional deregister callback, removes the timer, and tears down sysctls.
- `et_change_frequency()` delegates active timer frequency changes to `cpu_et_frequency()`.
- `et_find()` searches inactive timers by name, quality, and required flag bits.
- `et_init()` marks a timer active and installs event/deregister callbacks and callback argument.
- `et_start()` validates active state, one-shot/periodic capability constraints, clamps first/period values to min/max, and calls the hardware start method.
- `et_stop()`, `et_ban()`, and `et_free()` stop, disable capabilities, and deactivate timers.
- Exposes `kern.eventtimer.choice` sysctl showing available timers and qualities.

## Dependencies And Integration
Used by machine/platform event timer drivers and CPU timer management. Exposes timer metadata under `kern.eventtimer.et.<name>` sysctls.

## Risk Notes
Timer registration ordering controls default selection. Start-time validation catches capability mismatches with assertions, so incorrect driver flags can panic debug kernels or misconfigure timer behavior.
