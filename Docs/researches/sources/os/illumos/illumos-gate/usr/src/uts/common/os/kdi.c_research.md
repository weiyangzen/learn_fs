# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kdi.c

## Role

`kdi.c` is a small kernel debugger interface glue file. It forwards kernel lifecycle notifications to the active debugger vector and arbitrates DTrace versus KMDB breakpoint ownership.

## Debug Vector Forwarding

The global `kdi_dvec` contains debugger callbacks. This file forwards:
- VM-ready and memory-available notifications.
- Module-available and thread-available notifications.
- Module loaded/unloading notifications.
- x86 fault handling.
- SPARC CPU initialization and CPR restart hooks.

Some calls first invoke `dv_kctl_*` control callbacks, then the debugger-facing callback.

## DTrace/KMDB State

`kdi_dtrace_state` tracks one of idle, DTrace active, or KMDB breakpoint active.

`kdi_dtrace_set()` performs atomic compare-and-swap transitions for:
- DTrace activate/deactivate.
- KMDB breakpoint activate/deactivate.

It rejects conflicting ownership with `EBUSY`, treats idempotent transitions as success, and rejects invalid transition values with `EINVAL`.

## Research Notes

The file is simple but gates debugger/tracing coexistence. The main invariant is that DTrace and KMDB breakpoint activity cannot be active at the same time. The CAS loop avoids locking and makes the transition state safe under concurrent callers.
