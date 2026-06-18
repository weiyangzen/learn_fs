# sources/test-tools/stress-ng/stress-schedmix.c

Purpose: implements `schedmix`, a scheduler/interrupt stressor that forks multiple children, randomly changes scheduling policies and CPU affinities, and interleaves many small scheduling, sleep, syscall, semaphore, timer, and procfs workloads.

Important APIs/types/functions: `stress_schedmix_setaffinity()` best-effort pins a process to a CPU. `stress_schedmix_waste_time()` randomly selects one of many micro workloads: yields, nanosleeps, NOP loops, time reads, nice calls, prime lookup, getpid loops, fork/wait, rusage/times, pressure-file reads, semaphore contention with SIGSTOP/SIGCONT, select/pselect, membarrier, and affinity changes. `stress_schedmix_child()` changes scheduler policy and calls waste work. `stress_schedmix_info` exposes `schedmix-cpumix` and `schedmix-procs`.

Control flow: `stress_schedmix()` optionally discovers eligible CPUs, installs SIGXCPU ignore for deadline overrun, maps PID state, optionally maps a POSIX semaphore, resolves child count, forks children, and releases them after global sync. Each child may install a profiling timer, repeatedly selects a different scheduling policy from `stress_sched_types`, applies `sched_setscheduler()` or deadline `sched_setattr()`, tolerates common permission/unsupported errors, wastes time, increments bogo, and optionally changes CPU. The parent either pauses or randomly changes child affinity until stopped.

State and persistence: state is child processes, shared PID table, optional shared semaphore, optional CPU list, and profiling timer state. Cleanup destroys semaphore, kills/waits children, unmaps PID state, and frees CPU data.

Dependencies and integration points: depends on Linux/POSIX scheduling support, stress-ng scheduler type tables, affinity helpers, capabilities, mmap, killpid, prime, procfs discard helpers, optional POSIX semaphores, membarrier, select/pselect, and setitimer.

Risks and test signals: privilege-sensitive RT/deadline policies commonly fail with EPERM and are tolerated. The broad random workload makes reproduction harder but increases scheduler coverage. Signals are child exit status, no orphaned workers, bogo progress, and absence of unexpected scheduler syscall errors.
