# sources/test-tools/fio/eta.c

## Purpose
`eta.c` calculates and displays fio's live job status line: thread state map, percent complete, bandwidth, IOPS, rate limits, open file count, and ETA. It also exposes packed ETA data through `get_jobs_eta()`.

## Important APIs, Types, And Functions
Global buffers `__run_str` and `run_str` store raw and condensed thread states. `check_str_update()` maps `thread_data->runstate` and workload type to status characters. `eta_to_str()` formats seconds as day/hour/min/sec. `thread_eta()` estimates remaining seconds per job using total bytes, completed bytes, time-based limits, verify expansion, zone skip adjustments, ramp/start delay, fill-device sizing, and rate limits. `calc_rate()` and `calc_iops()` compute interval deltas. `calc_thread_status()` aggregates all jobs into `struct jobs_eta`. `display_thread_status()` renders the status line. `get_jobs_eta()`, `print_thread_status()`, and `print_status_init()` are external entry points.

## Control Flow
Status printing starts with `print_thread_status()`, which calls `get_jobs_eta(false)`. That allocates `jobs_eta`, calls `calc_thread_status()`, and sizes the result to the condensed run string. `calc_thread_status()` may skip work depending on output mode, stall state, TTY status, and ETA policy, unless forced. It walks all fio threads, updates counts/rate-limit sums/open files, computes per-thread ETA after an initial grace period, updates run-state characters, aggregates bytes/IOPS, periodically logs aggregate bandwidth samples, and calculates display-rate deltas. `display_thread_status()` builds a single carriage-return status line, pads over previous longer lines, and occasionally schedules a newline.

## State And Persistence
The file keeps static counters and timestamps for rate intervals and display formatting. It reads global fio state such as `thread_number`, `done_secs`, `eta_interval_msec`, output flags, aggregate log state, and all `thread_data` records. No durable state is persisted; output goes to stdout and aggregate logs through fio logging helpers.

## Dependencies And Integration Points
Dependencies include fio core globals/macros, time helpers, number formatting, aggregate logging, Valgrind DRD annotations, and power-of-two helpers. `struct jobs_eta` is part of fio's status/reporting interface and is compile-time checked against its packed form.

## Risks
ETA is heuristic and depends on many options; zone skip, verify, fill-device, stonewall, ramp, and time-based interactions are easy to regress. Several static arrays are global and not independently synchronized; DRD annotations only suppress one known variable. `calc_thread_status()` returns early after updating some static timing paths, so logging/display cadence is subtle.

## Test Signals
Tests should cover `eta_to_str`, condensed run string generation, runstate character mapping, time-based ETA, verify doubling/mixed write adjustment, zone skip adjustment, stonewall ETA accumulation, unified mixed reporting, TTY/ETA skip rules, aggregate bandwidth sample cadence, and packed `jobs_eta` sizing.
