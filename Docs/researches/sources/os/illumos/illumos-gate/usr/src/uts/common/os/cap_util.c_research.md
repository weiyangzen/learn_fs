# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cap_util.c

## Purpose

`cap_util.c` implements capacity/utilization measurement for processor hardware components using CPU performance counters. It programs per-CPU CPC contexts, samples counters, attributes utilization to CPUs and processor groups, exports per-CPU hardware-sharing kstats, and coordinates with DTrace CPC use and CPU online/offline events.

## Main Interfaces

Global control: `cu_init`, `cu_disable`, `cu_enable`.

Counter control: `cu_cpc_program`, `cu_cpc_unprogram`.

Updates: `cu_cpu_update`, `cu_pg_update`.

CPU lifecycle and helpers are mostly private: `cu_cpu_callback`, `cu_cpu_init`, `cu_cpu_fini`, `cu_cpu_disable`, `cu_cpu_enable`, `cu_cpu_run`, `cu_cpc_trigger`, `cu_cpu_update_stats`, `cu_cpu_kstat_create`, and `cu_cpu_kstat_update`.

## Behavior

`cu_init()` verifies the framework is enabled, initializes CPC support, allocates request storage, initializes per-active-CPU state, sets the module online, programs counters on active CPUs, and registers a CPU setup callback.

`cu_cpc_init()` determines which CPC events are needed. It first asks platform code through `cu_plat_cpc_init()`. If unsupported, common code walks the CPU’s CMT processor-group lineage and requests events such as `PAPI_tot_ins` for instruction pipeline groups and `PAPI_fp_ins` for FPU groups. It creates per-CPU/per-PG counter info and kstats.

`cu_cpu_init()` allocates `cpu_cu_info`, counter stats, and CPU-bound CPC contexts. `cu_cpu_fini()` deletes kstats, frees stats and CPC contexts, detaches `cpu_cu_info` via cross-call if needed, and frees the CPU state.

`cu_cpc_program()` runs on the target CPU at high PIL with preemption disabled. It refuses to program if CU is off, DTrace CPC is active, counters are already on, counters are disabled, or a live CPU CPC context exists. It rotates through prepared contexts, programs CPC counters, marks counters on, and samples initial state.

`cu_cpc_unprogram()` updates stats, validates that the current CPU CPC context is the CU context, unprograms counters, clears `cpu_cpc_ctx`, and marks counters off.

## Sampling And Kstats

`cu_cpu_update()` throttles sampling using `cu_update_threshold`. When sampling is needed, it reads CPC counters on the owning CPU either by cross-call or directly.

`cu_cpu_update_stats()` updates per-counter start values, deltas, running/stopped time, total utilization, current rate, and max rate. It handles off-to-on transitions by treating the current counter value as the new start.

`cu_cpu_kstat_update()` exports CPU id, PG id, generation, total utilization, running/stopped time, rate, max rate, and relationship string. Without `priv_cpc_cpu`, utilization values are zeroed.

`cu_pg_update()` aggregates all CPUs in a hardware processor group, updates each CPU first, sums utilization/time fields, accounts for stopped counters, and computes group rate/max rate.

## CPU And DTrace Coordination

`cu_disable()` and `cu_enable()` iterate active CPUs under `cpu_lock` and use CPU calls to toggle collection. `cu_cpc_trigger()` maintains a per-CPU disable count, unprogramming on first disable and reprogramming when the count returns to zero.

The CPU setup callback initializes state on `CPU_ON`, programs counters on `CPU_INTR_ON`, and disables/frees state on `CPU_OFF`.

DTrace CPC interaction is explicit: CU counters are not programmed while `dtrace_cpc_in_use` is true, and newly initialized CPUs start disabled when DTrace owns CPC.

## Notable Invariants

- CPC programming/unprogramming must run on the target CPU at high PIL with preemption disabled.
- `cpu_lock` protects CPU lifecycle initialization/finalization.
- `cpu_cu_info` must not be freed until target-CPU access is quiesced.
- Sampling is intentionally throttled to avoid excessive cross-calls.
- Kstat consumers need `priv_cpc_cpu` to see utilization data.
- CPU generation is exported so consumers can reject snapshots across topology changes.

## Dependencies

Depends on CPC/kcpc, CPU cross-calls, processor groups/CMT, platform CU hooks, DTrace CPC state, kstats, privilege checks, CPU lifecycle callbacks, high-resolution time, and hardware sharing relationship metadata.

## Research Notes

High-risk areas are target-CPU execution assumptions, interaction with thread-bound CPC contexts during CPU online, DTrace CPC disable/re-enable sequencing, cleanup of partially initialized CPU state, and rate calculations when CPUs go offline or counters stop mid-sample.
