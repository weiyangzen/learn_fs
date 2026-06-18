# sources/test-tools/stress-ng/stress-cpu-sched.c

## Purpose
This stressor aggressively exercises scheduler, affinity, priority, process, timer, and optional NUMA policy paths. It creates many child processes per worker, repeatedly changes their CPU affinity and scheduling policy, sends stop/continue signals, forks and execs short-lived children, and gathers scheduler-related side effects through `/proc` and debugfs reads.

## Important APIs, Types, And Functions
`stress_cpu_sched_info` exports the stressor when scheduling and `sched_setscheduler()` support exist. `stress_cpu_sched_nice()` adjusts priority and Linux autogroup. `stress_cpu_sched_setaffinity()` and `stress_cpu_sched_setscheduler()` are the core mutators, covering normal policies, reset-on-fork variants, realtime policies, and `SCHED_DEADLINE` through `shim_sched_setattr()`. `stress_cpu_sched_set_handler()` installs an optional realtime-timer signal handler that perturbs scheduling from `SIGRTMIN`. `stress_cpu_sched_fork()` and `stress_cpu_sched_exec()` exercise fork/exec paths. `stress_cpu_sched_child()` owns child creation and the parent control loop.

## Control Flow
`stress_cpu_sched()` discovers affinity-capable CPUs, allocates optional NUMA masks, lowers OOM priority, synchronizes, and runs `stress_cpu_sched_child()` through `stress_oomable_child()`. The child reads `cpu-sched-procs`, creates up to 1024 children, and each child loops through yields, nanosleeps, priority changes, `getcpu()`, nop loops, optional `set_mempolicy()`, and random affinity changes until timeout or stop. The controller shuffles pid order, optionally `SIGSTOP`s each child, changes affinity and scheduler policy, resumes it, updates priority, pulses extra stop/continue signals, periodically probes load/rusage/scheduler files, occasionally forks an exercising subprocess, and occasionally execs stress-ng with `--exec-exit`.

## State And Persistence
Global static state includes the child pid array, discovered CPU list, optional POSIX timer id, and optional NUMA mask. Per-run state is mostly process-tree and kernel scheduler state; it is not intended to persist beyond the stressor. Child pids are killed on exit through `stress_kill_and_wait_many()`, and affinity CPU memory/NUMA masks are freed.

## Dependencies And Integration Points
Dependencies include Linux/POSIX scheduling APIs, affinity helpers, capability checks, realtime timer APIs, signal handling, process kill helpers, NUMA helpers, OOM wrappers, load/rusage shims, `/proc/pressure/*`, `/proc/schedstat`, and `/sys/kernel/debug/sched/debug`. The stressor is classified as scheduler and OS work and exposes `cpu-sched-procs`.

## Risks
This code intentionally exercises privileged and error-heavy paths; realtime/deadline policy changes can fail or affect host responsiveness, and high process counts can exhaust pids or memory. The hrtimer signal handler calls limited stress-ng helpers while preserving `errno`; any unsafe expansion would be risky. NUMA policy and scheduler command availability vary by kernel. Correct cleanup of stopped children is essential, otherwise children could remain paused or running.

## Test Signals
Run with low and high `cpu-sched-procs`, with and without `CAP_SYS_NICE`, across kernels with different policy sets. Signals include no leaked child processes, no stuck `SIGSTOP` children, graceful fallback for unsupported realtime/deadline features, bogo progress, and scheduler/debugfs/proc probes not causing hard failures. Lockdep, scheduler tracepoints, and OOM handling are useful external signals.
