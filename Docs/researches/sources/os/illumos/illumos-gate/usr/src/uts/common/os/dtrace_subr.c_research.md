# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dtrace_subr.c

## Purpose

`dtrace_subr.c` contains small genunix-side DTrace integration hooks. It declares function pointers populated by DTrace-related modules, maintains high-resolution time snapshots safe for probe context, tracks DTrace virtual time state, and forwards fasttrap fork handling.

## Main Interfaces And Globals

Module hook pointers include:

- `dtrace_cpu_init`
- `dtrace_modload`
- `dtrace_modunload`
- `dtrace_helpers_cleanup`
- `dtrace_helpers_fork`
- `dtrace_cpustart_init`
- `dtrace_cpustart_fini`
- `dtrace_cpc_fire`
- `dtrace_closef`
- debugger init/fini hooks

Global state includes `dtrace_vtime_active`, `dtrace_predcache_id`, and `dtrace_cpc_in_use`. The CPC usage counter is documented as being coordinated by DTrace, CPC framework, CPU management, and `kcpc_cpuctx_lock`.

## High-Resolution Time Snapshots

DTrace probe context cannot safely acquire `hres_lock`, because probes may fire while that lock is already held. The file solves this by maintaining two `dtrace_hrestime_t` snapshots, each protected by a low-level lock word.

`dtrace_hres_tick()` runs from the same high-level cyclic context as `hres_tick()`. It updates both snapshots in succession:

1. Acquire the real high-resolution clock lock.
2. Copy `hrestime`, `hrestime_adj`, and current hrtime.
3. Release the clock lock.
4. Lock one DTrace snapshot, publish the copied values, issue a producer barrier, and unlock by incrementing the lock word.

Because one thread updates the two snapshots sequentially, at least one snapshot should be stable for probe readers.

`dtrace_gethrestime()` reads snapshot zero or one using lock-word parity and memory barriers. Once it has a stable snapshot, it computes nanoseconds from the copied `timestruc_t`, adds elapsed hrtime since the snapshot, and applies bounded `hrestime_adj` correction.

## Virtual Time

`dtrace_vtime_enable()` atomically transitions `dtrace_vtime_active` from inactive to active and panics if already active. `dtrace_vtime_disable()` performs the reverse and panics if already inactive.

`dtrace_vtime_switch()` disables interrupts, accounts elapsed virtual time to the outgoing current thread if it had a nonzero DTrace start timestamp, assigns the same timestamp to the incoming thread, and restores interrupts.

## Fasttrap Integration

`dtrace_fasttrap_fork()` is called from process fork handling when the parent appears to have active user-space DTrace tracepoints. It asserts the process lock and positive tracepoint count, then calls the loaded fasttrap module through `dtrace_fasttrap_fork_ptr`.

## Dependencies

This file depends on DTrace core headers, atomic operations, process structures, module-control structures, high-resolution clock globals, and fasttrap module hooks. SPARC builds include privileged-register definitions.

## Notable Invariants And Audit Notes

- `dtrace_gethrestime()` depends on the two-snapshot update protocol; both snapshot locks must not be held simultaneously by different writers.
- Memory barriers around snapshot publication and consumption are essential for probe-context readers.
- Virtual time enable/disable is single-owner state and intentionally panics on double enable or double disable.
- Fasttrap fork forwarding assumes the fasttrap module remains loaded when `p_dtrace_count > 0` under `P_PR_LOCK`.
