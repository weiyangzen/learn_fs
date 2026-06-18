# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lockstat_subr.c

## Purpose

`lockstat_subr.c` provides resident kernel support for the lockstat driver and DTrace lockstat probes.

It is intentionally small: it defines shared lockstat probe state and one helper that counts threads currently marked for lockstat tracing.

## Main Interfaces

Global state:

- `lockstat_probemap[LS_NPROBES]`
- `lockstat_probe`

Function:

- `lockstat_active_threads()`

## Behavior

`lockstat_probemap` maps lockstat probe indexes to DTrace probe IDs. `lockstat_probe` is a function pointer used by lock instrumentation paths to fire probes when lockstat is active.

`lockstat_active_threads()` counts active threads that have `t_lockstat` set. It enters `pidlock`, starts with `curthread`, walks the circular global thread list using `t_next`, increments a counter for each marked thread, and releases `pidlock`.

## Concurrency

`pidlock` protects traversal of the global thread list. The function assumes the thread list is circular and reaches `curthread` again to terminate.

## Dependencies

Depends on thread structures, CPU/kernel headers, cyclic/time headers, SPL definitions, and `sys/lockstat.h`.

## Research Notes

The main invariant is safe global thread-list traversal under `pidlock`. This file has no allocation, no user copy, and no complex lifecycle; most lockstat behavior lives in the lockstat driver and instrumentation users of `lockstat_probe`.
