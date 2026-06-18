# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuvar.h

## Role

Defines the central `cpu_t` per-CPU kernel structure, CPU state flags, CPU-set manipulation APIs, CPU lifecycle APIs, and per-CPU statistics macros.

## Core Per-CPU Structures

- `ftrace_data_t`: per-CPU fast event tracing state.
- `cpu_t`: large per-CPU state structure containing:
  - CPU ids and flags.
  - self pointer and current/idle/pause threads.
  - LWP/FPU owner state.
  - CPU partition, lgroup load, CPU PG membership.
  - CPU list links across global, online, partition, lgroup, and load partitions.
  - dispatch queue and scheduler/preemption state.
  - interrupt stack/thread/activity/base SPL state.
  - per-CPU statistics and CPU info kstat.
  - profiling PCs and PIL.
  - ftrace state.
  - deadman counters.
  - CPC performance counter context and lock.
  - `processor_info` data and CPU state start time.
  - CPR flags.
  - cyclic subsystem data.
  - networking squeue set.
  - pool properties.
  - DTrace fasttrap/probe accounting.
  - microstate accounting and load average.
  - debug id/brand strings.
  - interrupt weight, VM data, physical IDs.
  - current/supported frequencies.
  - CPC profiling PCs.
  - interrupt load tracking.
  - per-CPU pseudo-random rotor.
  - capacity/utilization info.
  - CPU generation for online/offline changes.
  - architecture-specific `machcpu` tail under `_MACHDEP`.

The file warns that adding members can affect CTF uniquification; new members must be added before `cpu_m_pad`.

- `cpu_core_t`: context-safe per-CPU state for DTrace flags, DCPC interrupt state, illegal value, and pid provider lock, padded to avoid false sharing.

## Interrupt and Random Macros

- `CPU_ON_INTR(cpup)`
- `INTR_ACTIVE(cpup, level)`
- `CPU_PSEUDO_RANDOM()`
- `INTR_STACK_SIZE`

## CPU Flags

Defines core CPU lifecycle/state flags:

- `CPU_RUNNING`
- `CPU_READY`
- `CPU_QUIESCED`
- `CPU_EXISTS`
- `CPU_ENABLE`
- `CPU_OFFLINE`
- `CPU_POWEROFF`
- `CPU_FROZEN`
- `CPU_SPARE`
- `CPU_FAULTED`
- `CPU_DISABLED`

Also defines `CPU_ACTIVE()` and `CPU_FORCED`.

## DTrace and Dispatcher Flags

- DTrace flags cover no-fault, drop, bad address/alignment, divide by zero, illegal op, no scratch, privilege faults, tuple overflow, entry/bad stack, and SPARC fake restore.
- Aggregate masks:
  - `CPU_DTRACE_FAULT`
  - `CPU_DTRACE_ERROR`
- Dispatcher flags:
  - `CPU_DISP_DONTSTEAL`
  - `CPU_DISP_HALTED`

## CPU Sets

- `cpuset_t`: opaque or concrete bitmap depending on `_MACHDEP`.
- APIs for allocation/free, all/all-but/only, add/delete, atomic add/delete, exclusive atomic add/delete, or/xor/and/zero, equality/null tests, find, bounds, membership.
- `_MACHDEP` compatibility macros wrap these APIs.

## CPU Globals

Includes arrays/lists and counters:

- `cpu[]`, `cpu_seq`, `cpu_list`, `cpu_active`, `cpu_active_set`
- `ncpus`, `ncpus_online`, `ncpus_intr_enabled`
- boot/max CPU counters and max ids
- `cpu_inmotion`, `clock_cpu_list`, `max_cpu_seqid_ever`
- `CPU` macro maps to `curcpup()` on x86 and `curthread->t_cpu` elsewhere.

## CPU Statistics

- `CPU_STATS_ENTER_K()`, `CPU_STATS_EXIT_K()`
- `CPU_STATS_ADD_K()`
- `CPU_STATS_ADDQ()`: emits DTrace probe then increments stat.
- `CPU_STATS()`
- `CPU_NEW_GENERATION()`: increments online/offline generation.

## CPR CPU Flags

- `CPU_CPR_OFFLINE`, `CPU_CPR_ONLINE`
- `CPU_CPR_IS_OFFLINE()`, `CPU_CPR_IS_ONLINE()`, `CPU_SET_CPR_FLAGS()`

## CPU Lifecycle and Scheduling APIs

Declares routines for CPU list management, active list management, kstats, visibility by zone, interrupt stats, cross-call mailbox init, poking CPUs, pausing/restarting CPUs, online/offline/spare/faulted/power state transitions, interrupt routing enable/disable/count, state checks, processor_info state strings, CPU clock/frequency strings, configure/unconfigure, bound thread destruction, CPU binding/unbinding, thread affinity, migration control, weak binding, and interrupt participation.

## CPU Setup Events

- `cpu_setup_t`: `CPU_INIT`, `CPU_CONFIG`, `CPU_UNCONFIG`, `CPU_ON`, `CPU_OFF`, `CPU_CPUPART_IN`, `CPU_CPUPART_OUT`, `CPU_SETUP`, `CPU_INTR_ON`.
- `cpu_setup_func_t`
- Registration/notification APIs:
  - `register_cpu_setup_func()`
  - `unregister_cpu_setup_func()`
  - `cpu_state_change_notify()`

## Research Relevance

One of the most important kernel headers in this batch. It anchors CPU scheduling, CPU hotplug, interrupt routing, DTrace state, power/current frequency accounting, zones visibility, processor sets, and per-CPU statistics that filesystem and block-layer performance work often depends on.
