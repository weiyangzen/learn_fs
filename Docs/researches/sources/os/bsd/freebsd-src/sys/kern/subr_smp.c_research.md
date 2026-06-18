# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_smp.c

## Purpose

`subr_smp.c` contains machine-independent SMP support: global CPU state, SMP startup coordination, CPU stop/restart helpers, cross-CPU rendezvous, CPU topology construction and analysis, CPU quiescing helpers, and a sequential-consistency fence broadcast.

It also provides dummy-compatible behavior for UP kernels so modules can call SMP APIs regardless of kernel configuration.

## Global State

Important exported/global state includes:

- `all_cpus`: set of CPUs known to the kernel.
- `mp_ncpus`, `mp_maxcpus`, `mp_maxid`, `mp_ncores`.
- `smp_started`, `smp_disabled`, `smp_cpus`, `smp_threads_per_core`.
- Under SMP: `stopped_cpus`, `started_cpus`, `suspended_cpus`, `hlt_cpus_mask`, `logical_cpus_mask`.
- `stoppcbs`: PCB snapshots saved during panic/stop handling.
- `smp_ipi_mtx`: spin mutex serializing rendezvous and TLB shootdown style busy-wait IPI operations.

Sysctls under `kern.smp` expose active state, CPU counts, max IDs, topology override, and disable state.

## Startup

`mp_setmaxid()` calls machine-dependent `cpu_mp_setmaxid()` very early, validates CPU counters, and sizes cpusets.

`mp_start()` initializes the IPI mutex, checks loader disable/probe result, falls back to one CPU if needed, otherwise calls machine-dependent startup, logs CPU count, allocates `stoppcbs`, and announces CPUs.

UP builds initialize CPU variables with `mp_setvariables_for_up()`.

`forward_signal(td)` sends `IPI_AST` to a running thread on another CPU so it processes pending AST/signal state.

## Stop, Suspend, And Restart

`generic_stop_cpus(map, type)` sends stop/suspend/offline IPIs, serializes concurrent stop operations with a static `stopping_cpu`, and spins until target CPUs report stopped/suspended or a timeout message is printed. x86 suspend/offline paths also take `smp_ipi_mtx` to avoid lost IPI assumptions under virtualization.

Public wrappers include `stop_cpus()`, `stop_cpus_hard()`, and on x86 `suspend_cpus()` / `offline_cpus()`.

`generic_restart_cpus(map, type)` signals stopped/suspended CPUs to resume and waits for stop bits to clear. For normal stop on x86 it also writes monitor buffers to wake CPUs stopped with MWAIT. Public wrappers include `restart_cpus()` and x86 `resume_cpus()`.

## Rendezvous

`smp_rendezvous_cpus(map, setup_func, action_func, teardown_func, arg)` runs callbacks on a CPU set with barriers before action and before teardown unless the callback is `smp_no_rendezvous_barrier`. It:

- Executes locally with spinlock protection before SMP starts.
- Requires interrupts/spinlock state suitable to avoid IPI mutex livelock.
- Intersects the requested map with `all_cpus`.
- Serializes rendezvous with `smp_ipi_mtx`.
- Stores callback parameters in global rendezvous variables.
- Sends `IPI_RENDEZVOUS` to remote CPUs.
- Runs the action on the current CPU if selected.
- Waits for all participants to release-complete.

`smp_rendezvous_action()` is the target-side routine. It uses atomic wait counters, fetches callback state after an acquire barrier, wraps callbacks in a special critical-section pattern, and release-signals completion.

`smp_rendezvous_cpu()` and `smp_rendezvous()` are convenience wrappers.

`smp_rendezvous_cpus_retry()` repeats rendezvous over a CPU set until participants clear themselves through `smp_rendezvous_cpus_done()`, calling a supplied wait function for CPUs that did not complete.

## Topology Helpers

`smp_topo_alloc()` allocates persistent `cpu_group` storage. `smp_topo_none()` builds a flat topology.

`smp_topo()` lazily builds topology once, using a debug override from `kern.smp.topology` or machine-dependent `cpu_topo()`. It validates CPU count and mask against `all_cpus`, collapses single-child levels, fills first/last CPU fields, and returns the root.

`smp_topo_1level()` and `smp_topo_2level()` construct synthetic package/cache/core groupings. `smp_topo_find()` locates the smallest group containing a CPU.

Under SMP, `topo_node` helpers manage richer topology trees: initialization, child add/find by hardware ID, child promotion by rotation, depth-first traversal, PU logical ID assignment, and uniformity analysis through `topo_analyze()`.

## Quiescing And Fences

`quiesce_cpus(map, wmesg, prio)` either waits for selected idle threads to switch once or, with `PDROP`, forces context switches by binding the current thread across CPUs. `quiesce_all_cpus()` targets all CPUs.

`quiesce_all_critical()` spins until every CPU’s current thread is outside a critical section, or until the current thread changes, indicating the critical path exited.

`cpus_fence_seq_cst()` forces a sequentially consistent fence on all CPUs using rendezvous under SMP, or locally under UP.

## Maintenance Notes

The rendezvous implementation relies on global pseudo-structure variables guarded by `smp_ipi_mtx` and atomic barriers. Callback functions must be reentrant and safe in unknown lock context, as documented in the file.

Stop/restart paths are architecture-sensitive. x86 has extra suspend/offline and NMI-broadcast behavior; non-x86 paths are simpler. Any change here needs architecture-specific review.
