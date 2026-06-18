# sources/test-tools/stress-ng/stress-cyclic.c

## Purpose
This stressor measures cyclic scheduling/timer latency under selectable sleep mechanisms and scheduler policies. It is both a benchmark and a scheduler stressor: it attempts realtime or other policies, gathers latency samples, reports summary statistics and percentiles, and can print latency distribution buckets.

## Important APIs, Types, And Functions
`stress_policy_t` describes scheduler policies and whether `CAP_SYS_NICE` is required. `stress_rt_stats_t` stores latency samples, min/max/mean/mode/stddev, priority bounds, and sample counts. Sleep methods include `stress_cyclic_clock_nanosleep()`, `stress_cyclic_posix_nanosleep()`, `stress_cyclic_poll()`, `stress_cyclic_pselect()`, `stress_cyclic_itimer()`, and `stress_cyclic_usleep()`. `stress_cyclic_stats()` records one latency. `stress_rt_stats()` sorts and summarizes samples. `stress_rt_dist()` prints histograms. `stress_cyclic()` is the main runner.

## Control Flow
Initialization maps a shared state object and creates a lock to throttle repeated scheduler error messages. `stress_cyclic()` reads distribution, method, policy, priority, sample count, and sleep interval options; validates method and policy availability; checks `CAP_SYS_NICE` for realtime policies; forces a default timeout if none was set; maps shared stats and latency arrays; computes scheduler priority bounds; and synchronizes. It forks a child so CPU and realtime limits can kill only the measurer. The child sets `RLIMIT_CPU` and optional `RLIMIT_RTTIME`, installs `SIGXCPU` handling, attempts the requested scheduler policy, then loops calling the selected cyclic method and incrementing bogo count until stop or timeout. The parent applies scheduler settings to itself, pauses, kills/waits for the child, then computes and prints statistics.

## State And Persistence
State is shared anonymous memory for global error count, runtime statistics, and latency samples. No external files are persisted. The report includes scheduler policy, optional sched-ext op name, requested delay, sample count, mean, mode, min, max, standard deviation, percentile samples, optional distribution, and a note if more sample storage was needed.

## Dependencies And Integration Points
Dependencies include POSIX clocks, timers, nanosleep, pselect/select availability, scheduler policy APIs, capability checks, rlimit handling, signal/longjmp helpers, shared mmap, stress-ng lock helpers, sorting, and process kill helpers. Options expose cyclic distribution, method, policy, priority, sleep duration, and sample count.

## Risks
Realtime policies can require privileges and can affect host scheduling. The child may be killed by CPU or realtime limits, so cleanup and parent reporting must tolerate partial samples. The `poll` method busy-waits and consumes CPU. Latency arrays can be large up to 100 million samples, so allocation failure must be handled. Percentile indexing assumes nonzero sample count and sorted samples. Scheduler support varies sharply by kernel, especially `SCHED_DEADLINE` and `SCHED_EXT`.

## Test Signals
Signals include skip behavior for missing policies or missing `CAP_SYS_NICE`, successful stats for every advertised method, correct fallback when `SCHED_DEADLINE` attr size is unsupported, bounded repeated scheduler error logging, distribution output when requested, and correct cleanup of mapped stats/latency regions. One-instance runs are the best benchmark signal; multi-instance runs are more useful for scheduler stress.
