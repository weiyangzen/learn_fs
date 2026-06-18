# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msacct.c

## Purpose

`msacct.c` implements illumos microstate accounting for LWPs/threads and CPUs. It tracks high-resolution time spent in execution, sleep, stopped, fault, wait-CPU, user, system, and idle states, and derives recent CPU percentage from those transitions.

Read completely: 849 lines.

## Main Responsibilities

- Initializes and terminates per-LWP microstate accounting.
- Initializes, transitions, and disables per-CPU microstate accounting.
- Updates thread and CPU state on syscall, trap, dispatcher, sleep, stop, and termination paths.
- Aggregates process and thread microstate times.
- Maintains zone user/system/wait CPU accounting arrays.
- Computes decayed/grown recent CPU percentage values.

## Thread And CPU State Initialization

`init_mstate()` initializes an LWP-backed thread's `lwp_mstate`, starting timestamp, previous state, current thread state, wait-runqueue timestamp, and accounting arrays. Kernel threads without LWPs are skipped by later accounting paths.

`init_cpu_mstate()` initializes CPU state, start timestamp, runqueue wait total, and CPU accounting arrays. `term_cpu_mstate()` switches a CPU to `CMS_DISABLED`, a placeholder state not accumulated as active time.

## CPU Microstate Transitions

`new_cpu_mstate()` changes the current CPU among `CMS_USER`, `CMS_SYSTEM`, and `CMS_IDLE`. It is intentionally lockless because only the local CPU updates its own state. Readers rely on `cpu_mstate_gen`, which is set to zero during updates and restored to a non-zero generation afterward.

The file documents that this depends on TSO or equivalent store ordering. The update path avoids producer barriers because syscall transitions are performance-critical.

## Thread Accounting Paths

`syscall_mstate()` handles common user/system syscall transitions, charges elapsed time to the old LWP state, updates zone user/system counters, and updates the current CPU microstate while preemption is disabled.

`new_mstate()` is the general LWP state transition function. It accounts elapsed time in the old state, maps several fault and user-lock states into system accounting, updates recent CPU percentage, remembers the previous runnable state, updates zone counters, and switches CPU state when appropriate.

`restore_mstate()` is called by the dispatcher when selecting a thread. It accounts sleep or stopped time, restores the previous runnable state, clears `t_waitrq`, charges wait-CPU time, and updates per-zone and per-CPU wait totals.

`term_mstate()` finalizes an exiting LWP by switching it to stopped, scaling all microstate accumulators into process totals, transferring resource usage counters, adding elapsed real time, and incrementing the defunct LWP count.

## Aggregation And CPU Percent

`mstate_thread_onproc_time()` returns scaled user+system+trap on-processor time for a thread, including current in-flight state time where applicable.

`mstate_systhread_times()` returns system-thread on-processor and runnable time, noting that unlocked fields make this interface inherently race-prone and not strictly monotonic.

`mstate_aggr_state()` aggregates a process state from process-level exited-LWP accounting plus live thread accounting.

`exp_x()`, `cpu_decay()`, `cpu_grow()`, and `cpu_update_pct()` implement recent CPU percentage as a scaled exponential decay/growth function. `cpu_update_pct()` uses atomic CAS because it can be called at elevated PIL and cannot safely take locks.

## Locking And Ordering

- Process aggregation requires `p_lock`.
- Some thread-time readers assert `THREAD_LOCK_HELD(t)` but document that self-updated fields can still race.
- CPU microstate updates require preemption disabled when tied to current thread CPU.
- CPU state readers must use generation checks and consumer barriers outside this file.
- CPU microstate writes rely on volatile fields and TSO-like ordering.

## Notable Edge Cases

- Negative elapsed time can occur from inconsistent unscaled high-resolution timestamps across CPUs; loops retry with a fresh timestamp.
- The initial startup thread may have `ms_state_start == 0`, so zone accounting skips that initial span.
- Interrupt threads that pin another thread are excluded from LWP microstate updates.
- `mstate_systhread_times()` explicitly warns its results can temporarily decrease or be too large.
- Fault and user-lock microstates may contribute to `LMS_SYSTEM` aggregation depending on context.

## Research Relevance

This file is not filesystem-specific, but it is relevant to performance research. Filesystem and storage workloads consume these accounting paths for system time, runqueue wait time, process resource accounting, zone usage, and CPU percentage metrics visible through proc/stat tooling.
