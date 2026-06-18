# sources/test-tools/stress-ng/stress-schedpolicy.c

Purpose: implements `schedpolicy`, a scheduler policy stressor that cycles or randomly selects available scheduling policies for the current process, probes `sched_*` error paths, and records per-policy schedule rates.

Important APIs/types/functions: `stress_schedpolicy_info` exposes `schedpolicy-cpumix` and `schedpolicy-rand`. The stressor uses `stress_sched_types[]` from core scheduling integration, `sched_setscheduler()`, `sched_getscheduler()`, `sched_getparam()`, `sched_setparam()`, and Linux `sched_getattr()`/`sched_setattr()` shims. Optional util-clamp handling is guarded by `USE_CLAMP`.

Control flow: `stress_schedpolicy()` allocates per-policy counters, optionally discovers CPUs, decides sequential versus random policy selection, synchronizes, and loops. For each policy it handles deadline attributes, normal policies, and FIFO/RR priorities, including invalid syscall probes. Successful sets optionally change CPU affinity and verify with `sched_getscheduler()` when the policy metadata says it is checkable. Periodic blocks exercise invalid get/setparam calls, bad PIDs, oversized attrs, invalid flags, and util-clamp value cycling.

State and persistence: state is process-local counters, util-clamp min/max tracking, CPU list, and timing. No filesystem state is created.

Dependencies and integration points: requires Linux/POSIX scheduling support and excludes unsupported OSes. It integrates with stress-ng capabilities checks for `CAP_SYS_NICE`, affinity helpers, scheduler metadata, unused-PID helper, metrics, sync, and stop flags.

Risks and test signals: behavior is heavily privilege and kernel-version dependent; EPERM/EINVAL/ENOSYS/E2BIG/EBUSY are expected in many branches. Verification failures occur when a successfully applied policy is not reflected by `sched_getscheduler()`. Metrics report schedules per second per policy.
