# sources/test-tools/fio/idletime.c

## Purpose
Implements fio's CPU idle profiler. It calibrates a small CPU-bound memory-touch workload on each CPU, optionally runs low-priority per-CPU profiler threads during a job, then reports inferred CPU idleness as normal or JSON output.

## Important APIs, Types, and Functions
Public functions are `fio_idle_prof_parse_opt`, `fio_idle_prof_init`, `fio_idle_prof_start`, `fio_idle_prof_stop`, `show_idle_prof_stats`, and `fio_idle_prof_cleanup`. Global profiler state lives in volatile `ipc` (`struct idle_prof_common`). Worker state is `struct idle_prof_thread`. Internal helpers include `calibrate_unit`, CPU affinity setup/free, `idle_prof_thread_fn`, `calibration_stats`, and `fio_idle_prof_cpu_stat`.

## Control Flow
Option parsing accepts `calibrate`, `system`, or `percpu` only when CPU affinity and idle scheduling support exist. Initialization allocates one thread record and one page-sized buffer per CPU, initializes locks/condition variables, locks per-thread gates, creates detached worker threads, releases the initialization gates, waits for calibration, and computes mean/stddev. Start unlocks the profiling gates. Stop sets `IDLE_PROF_STATUS_PROF_STOP`, waits for worker exit, and computes idleness from loop count, calibrated unit time, and elapsed runtime. Stats are then printed or added to JSON.

## State and Persistence Behavior
No persistent files are written. `ipc` stores selected option, CPU count, calibration stats, buffers, thread records, and status. Threads are detached, so cleanup only frees the arrays after stop/stat collection. Calibration-only mode runs init/start/stop immediately and returns a command-line early-exit signal.

## Dependencies and Integration Points
Depends on fio timing, logging, JSON output, CPU affinity wrappers, scheduler idle support, `page_size`, and thread state constants. It is wired through `parse_cmd_line()` via `--idle-prof` and through normal output generation.

## Risks
The code aborts profiling if any CPU thread fails, which is accurate but fragile on constrained systems. `calibration_stats()` divides by `nr_cpus - 1`; single-CPU systems risk invalid standard-deviation math. Detached worker threads plus mutex-gated lifecycle require careful ordering. `ipc.status` is volatile shared state, not a full atomic protocol. CPU affinity or idle scheduling failures disable profiling on otherwise valid runs.

## Test Signals
Tests should cover unsupported-platform option errors, calibration-only output, system/percpu JSON fields, single-CPU behavior, thread creation failure paths, and start/stop cleanup under sanitizers. Integration signals are stable `CPU idleness` output and no lingering profiler threads after fio exits.
