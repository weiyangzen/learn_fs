# File Research: sources/os/bsd/freebsd-src/sys/kern/sched_shim.c

## Purpose
Provides the scheduler dispatch shim that routes the public `sched_*` kernel API to the active runtime-selected scheduler instance. It also defines shared scheduler probes/statistics and sysctls describing scheduler selection and CPU topology.

## Key Elements
- `const struct sched_instance *active_sched` is the selected scheduler implementation.
- `DEFINE_SHIM*` macros generate IFUNC-backed public scheduler entry points that return the matching function pointer from `active_sched`.
- Shimmed functions cover load, round-robin interval, fork/exit, priority changes, sleep/wakeup, run queue operations, CPU binding/affinity, timer accounting, topology helpers, and scheduler initialization hooks.
- Scheduler SDT probes and scheduler statistics are defined here so all scheduler implementations share the same instrumentation names.
- DTrace virtual-time hook globals are defined under `KDTRACE_HOOKS`.
- `sched_name` defaults to `"ULE"` and can be overridden by the `kern.sched.name` tunable.

## Scheduler Selection
`sched_instance_select()` scans the `sched_instance_set` linker set for a name matching `sched_name`. If none matches, it selects the first compiled-in scheduler and copies that scheduler's name into `sched_name`. `schedinit()` panics if selection failed; otherwise it calls the selected scheduler's `init()`.

## Sysinit and Sysctl Behavior
- `sched_setup()` runs at `SI_SUB_RUN_QUEUE`, records CPU topology from `smp_topo()`, and calls `active_sched->setup()`.
- `sched_initticks()` runs after clocks initialize and calls `active_sched->initticks()`.
- `sched_schedcpu()` starts periodic scheduler CPU accounting near the end of boot.
- `kern.sched.name` reports the active scheduler name.
- `kern.sched.available` reports comma-separated names from the scheduler linker set.
- `kern.ccpu` exposes the CPU decay factor.
- `kern.sched.topology_spec` emits an XML-like CPU topology dump from `cpu_top`.

## Filesystem / VM Relevance
The file is not filesystem-specific, but it determines which scheduler implementation all kernel threads, filesystem workers, storage interrupts, and VFS callers run under. The topology sysctl is relevant when analyzing workload placement and I/O-worker CPU behavior.

## Notable Edge Cases
- If the configured scheduler name is unavailable but at least one scheduler is compiled in, the shim silently falls back to the first linker-set entry.
- CPU topology output handles `cpu_top == NULL` by returning a minimal empty group.
- The IFUNC shims assume `active_sched` has been selected before the generated public functions are used.
