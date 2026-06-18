# sources/test-tools/stress-ng/stress-affinity.c

## Purpose
`stress-affinity.c` implements the `affinity` stressor, rapidly changing CPU affinity across multiple processes to exercise scheduler affinity APIs and CPU mask behavior.

## Important APIs, Types, And Functions
`stress_affinity_info_t` is a shared control block containing CPU count, selected CPU, delay/sleep settings, random mode, and pin mode. `stress_affinity_supported` probes `sched_getaffinity`/`sched_setaffinity`. `stress_affinity_child` performs the affinity-change loop. `stress_affinity_reap` kills/waits helper children. `stress_affinity` orchestrates shared memory, locks, child forking, sync-start, and cleanup. `stress_affinity_info` registers options such as `--affinity-delay`, `--affinity-pin`, `--affinity-procs`, `--affinity-rand`, and `--affinity-sleep`.

## Control Flow
The main stressor determines child count, mmaps shared PID and info blocks, creates a counter lock, reads options, forks children into slots 1..N-1, synchronizes start, then runs `stress_affinity_child` in the parent as pin controller. Each loop chooses a CPU sequentially or randomly, optionally shares a pinned CPU through the control block, calls `sched_setaffinity`, verifies with `sched_getaffinity` when enabled, exercises invalid syscall arguments, increments bogo ops under a lock, and applies spin/sleep delays.

## State And Persistence
State is anonymous shared memory for PID records and affinity control plus a process-shared counter lock. It changes only process CPU affinity masks and does not persist filesystem state.

## Dependencies And Integration Points
It depends on Linux/BSD-style CPU affinity APIs, `cpu_set_t` macros, sync-start helpers, mmap helpers, kill/wait helpers, lock helpers, option settings, and stress-ng verification flags. It is classified as `CLASS_SCHEDULER`.

## Risks
CPU hotplug and restricted cpusets can make selected CPUs invalid; the loop handles `EINVAL` retry cases but verification can still be noisy under taskset-random/aggressive modes. `CPU_SET` is limited by `cpu_set_t` capacity, while `stress_cpus_configured_get` may exceed that on very large systems. Cleanup must reap many children reliably.

## Test Signals
Direct runs with `--affinity`, `--affinity-pin`, `--affinity-rand`, `--affinity-sleep`, and different `--affinity-procs` validate behavior. Kernel coverage includes affinity option sweeps, and support probing should skip on systems where affinity cannot be set.
