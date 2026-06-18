# sources/test-tools/stress-ng/stress-softlockup.c

## Purpose

`stress-softlockup.c` implements `softlockup`, a privileged scheduler stressor intended to create CPU starvation/soft-lockup-like conditions. It forks one child per online CPU, gives them realtime scheduler policies at maximum priority when possible, drops niceness, and runs busy loops bounded by CPU/RT time limits.

## Important APIs, Types, and Functions

- `stress_softlockup_supported()` requires `CAP_SYS_NICE`.
- `stress_policy_t` describes supported realtime policies and their maximum priorities.
- `stress_softlockup_loop()` performs a memory-barrier-heavy no-op loop.
- `stress_softlockup_loop_count()` calibrates a loop count that takes roughly 0.01 seconds.
- `stress_softlockup_rep_stosb()` optionally runs x86 `rep stosb` over a shared 1 MiB buffer to add memory pressure.
- `stress_rlimit_handler()` handles CPU-time signals by clearing the continue flag and long-jumping out.
- `drop_niceness()` attempts to reduce nice level as far as permissions allow.
- `stress_softlockup_child()` applies rlimits, signal handling, realtime policy cycling, busy loops, and bogo increments.
- `stress_softlockup()` allocates child PID synchronization state, forks per CPU, starts children together, makes the parent realtime, pauses, then kills/waits children.

## Control Flow

The entry point calibrates the loop count, optionally maps the x86 `rep stosb` buffer, allocates a shared PID synchronization array sized to online CPUs, initializes per-child start gates, validates available scheduling policies, and records maximum priorities. It forks one child per online CPU with retry support. Each child waits on its per-PID start gate, sets failure injection and CPU affinity, then enters `stress_softlockup_child()`.

The child sets `RLIMIT_CPU` and optional `RLIMIT_RTTIME` to the global timeout, installs a `SIGXCPU` long-jump handler, drops niceness, cycles through realtime policies, sets max priority, runs a randomized number of calibrated busy loops, optionally performs the x86 memory-fill path, increments bogo operations, and exits when timeout or continue flags stop it. The parent synchronizes the global start, releases all children, sets its own scheduler to the first policy, pauses, then kills/waits all children with `SIGALRM`.

## State and Persistence Behavior

The stressor creates process-local global state for optional x86 buffer and the signal jump environment. It maps temporary shared memory for child synchronization and optional shared memory for `rep stosb`, both unmapped on cleanup. It changes scheduler policy and niceness of the stressor processes but does not persist system configuration.

## Dependencies and Integration Points

This file depends on `sched_get_priority_max()`, `sched_setscheduler()`, realtime policies such as `SCHED_FIFO` and `SCHED_RR`, rlimits, stress-ng capability checks, child synchronization helpers, affinity helpers, kill/wait helpers, and optional x86 assembly. It registers as `CLASS_SCHEDULER`, `VERIFY_ALWAYS`, with a `.supported` callback. Unsupported scheduler builds export unimplemented.

## Risks and Edge Cases

This is intentionally disruptive and requires `CAP_SYS_NICE`. Realtime children can starve other work until rlimits or external signals stop them; the code adds CPU/RT time bounds and parent kill logic to limit damage. Some systems may not support the compiled realtime policies or may report low maximum priorities. The parent calls `pause()` after becoming realtime, so correct signal delivery and child termination paths are important. If fork fails partway through, already-started PID records are cleaned up through the finish path.

## Test Signals

Primary test signals are skip behavior without `CAP_SYS_NICE`, successful policy priority discovery, child start synchronization, and clean termination at timeout. On capable systems, bogo counts should increase and no child should survive after the stressor exits. Tests should also cover kernels lacking `SCHED_FIFO` or `SCHED_RR` support.
