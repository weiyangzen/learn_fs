# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_psref.c

## Purpose
Implements passive references: CPU-local references that are cheap to acquire/release and expensive to drain, intended for objects whose destruction can wait for xcall-based global checks.

## Main Entry Points
- `psref_init()` initializes optional debug LWP-specific state.
- `psref_class_create()` and `psref_class_destroy()` manage reference classes.
- `psref_target_init()` and `psref_target_destroy()` initialize and drain/destroy reference targets.
- `psref_acquire()`, `psref_release()`, and `psref_copy()` manage individual stack-allocated `struct psref` references.
- `psref_held()` is a diagnostic predicate; `psref_debug_init_lwp()` and `psref_debug_barrier()` are available with `PSREF_DEBUG`.

## Control Flow And State
Each class owns a mutex/CV, a per-CPU `struct psref_cpu` list, an IPL cookie, and xcall flags. Acquiring a reference asserts the caller cannot migrate CPUs unless it is in softint or bound LWP context, raises to the class IPL, gets the current CPU's per-CPU list, inserts the `psref`, records target/LWP/CPU, and drops the per-CPU reference. Release performs matching target/LWP/CPU checks, removes from the current CPU list, updates diagnostic counters, and broadcasts if the target is draining.

Destroying a target sets `prt_draining` so new acquires assert, then repeatedly broadcasts a high-priority class xcall. Each CPU runs `_psref_held()` to see whether its local list contains the target. If any reference remains, the destroyer timed-waits on the class CV and retries until all references are gone, then clears `prt_class`.

## Dependencies
Built on `percpu`, xcalls, IPL raising, mutex/CV, LWP and CPU identity, SLIST queues, and optional LWP-specific debug storage.

## Risks And Notes
Passive references must not move across CPUs or LWPs; the code has explicit assertions for both. Callers must remove targets from discoverable data structures before `psref_target_destroy()` so no new references can be acquired. Target initialization requires the caller to publish with a producer memory barrier before other CPUs can find the target. Debug mode tracks per-LWP held references and can panic on leaks at barriers.
