# sources/test-tools/stress-ng/stress-dekker.c

## Purpose
This stressor validates and stresses Dekker-style mutual exclusion between two processes sharing memory. It uses volatile shared flags, a turn variable, explicit memory fences/barriers, and critical-section checks to expose weak memory ordering or broken barrier support.

## Important APIs, Types, And Functions
`dekker_mutex_t` stores `wants_to_enter[2]`, `turn`, and a shared `check` counter. `dekker_t` combines the mutex with cacheline-padded metrics for both participants. `stress_dekker_supported()` installs a temporary `SIGILL` handler and probes the architecture memory barrier. `stress_dekker_p0()` and `stress_dekker_p1()` implement the two halves of Dekker's algorithm. `stress_dekker()` maps shared memory, forks the peer process, runs both halves, combines metrics, and cleans up.

## Control Flow
The supported check uses `sigsetjmp()`/`siglongjmp()` to skip the stressor if the barrier instruction traps. Runtime maps a shared anonymous page, names it, zeros metrics, synchronizes, and forks. The child repeatedly enters participant 0's critical section, incrementing `check`; the parent repeatedly enters participant 1's critical section, decrementing `check` and incrementing bogo count. Both sides set their intent flag, fence/barrier, spin on the other flag and turn, enter the critical section, verify that the counter changed by exactly one, set the turn to the other participant, clear intent, and update timing metrics. Parent kills and waits for the child at exit.

## State And Persistence
State is one shared mmap region and a static pointer plus jump buffer. There is no filesystem persistence. The final metric is nanoseconds per mutex based on combined participant durations and counts.

## Dependencies And Integration Points
Dependencies include shim memory fences, optional ARM `dmb sy`, signal longjmp support, shared mmap, CPU affinity helper for the child, kill/wait helpers, and stress-ng metrics. If memory fencing or longjmp support is absent it registers as unimplemented.

## Risks
This is intentionally sensitive to memory ordering. Incorrect fence semantics can cause mutual exclusion failure and `check` mismatches. Spin loops can burn CPU and can run indefinitely if the peer dies without stop propagation. The fork-failure path should unmap shared memory; changes here should preserve cleanup. Cacheline padding assumes 64-byte intent to reduce metric contention.

## Test Signals
Signals include supported-probe skip on illegal barrier instructions, sustained bogo progress, zero mutex check failures, clean child termination, and plausible nanoseconds-per-mutex metrics. Running on weakly ordered architectures is the most valuable validation.
