# sources/test-tools/stress-ng/stress-min-nanosleep.c

Purpose: `stress-min-nanosleep.c` measures the shortest observed `nanosleep` delays for requested sleeps from 0 ns through powers of two up to a configured maximum. It stresses scheduler/timer behavior and fails verification if measured sleep duration is shorter than requested.

Important APIs/types/functions: `nanosleep_delay_t` stores requested ns, min/max observed ns, count, sum, mean, and update state. `nanosleep_delays_t` stores per-instance arrays plus pid/start/finish flags in shared memory. `stress_min_nanosleep_sched` optionally applies a requested scheduler policy, including special handling for deadline scheduling, FIFO/RR priorities, and fallback policies. `stress_min_nanosleep_init` and `stress_min_nanosleep_deinit` allocate/free the shared delay table.

Control flow: initialization maps one `nanosleep_delays_t` per instance. Each worker reads `--min-nanosleep-max` and `--min-nanosleep-sched`, applies scheduling if possible, initializes delay slots for 0 and powers of two, synchronizes, then loops. For each delay, it measures `NANOSLEEP_LOOPS` calls using `clock_gettime(CLOCK_MONOTONIC)` before and after, records per-call min/max/sum, and increments bogo operations. Instance zero waits for other instances to finish, aggregates all delay rows, prints a table, reports too-short sleeps, and prints the minimum measured sleep.

State and persistence behavior: all state is shared anonymous memory in `delays`. There is no filesystem persistence. Instance zero may wait on sibling pids recorded in the shared table to make sure aggregation sees finished data.

Dependencies and integration points: the file depends on `clock_gettime`, `CLOCK_MONOTONIC`, `nanosleep`, scheduler helpers and shim scheduler attributes, cpuidle headers, mmap helpers, and stress-ng init/deinit hooks. It registers `stress_min_nanosleep_info` with `.init`, `.deinit`, scheduler/interrupt/OS classifiers, `VERIFY_ALWAYS`, and max/scheduler options; unsupported builds register unimplemented.

Risks: timing measurements are sensitive to clock resolution, scheduler priority privileges, virtualization, CPU power states, and signal interruption. The aggregation wait loop depends on child pid bookkeeping and can stall if start/finish flags are mishandled. Deadline/real-time scheduler attempts must remain best-effort because insufficient privilege is common.

Test signals: run `stress-ng --min-nanosleep 1 --min-nanosleep-ops 1`, repeat with `--min-nanosleep-max 1024`, and try scheduler policies available on the host. Verify output should show no “too short” rows; unsupported scheduler changes should log informational messages without failing the stressor.
