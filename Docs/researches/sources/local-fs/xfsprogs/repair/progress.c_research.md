# File Research: sources/local-fs/xfsprogs/repair/progress.c

## Role

`progress.c` implements periodic and final progress reporting for xfs_repair phases. It maintains per-AG done counters, report message metadata, phase timestamps, a background timer thread, and summary duration output.

## Core Behavior

- `init_progress_rpt()` allocates `prog_rpt_done`, initializes `global_msgs`, and starts the reporting thread.
- `progress_rpt_thread()` waits for timer signals, sums progress counters, prints formatted status, and for selected phases prints rate/percentage/ETA.
- `set_progress_msg()` switches the active report format and resets counters.
- `print_final_rpt()` prints the current report’s final count.
- `timestamp()` records phase start/end times and optionally reports libxfs buffer cache state.
- `duration()` formats elapsed seconds into weeks/days/hours/minutes/seconds.
- `summary_report()` prints phase timing summaries.

## Data Model

`progress_rpt_reports` maps the progress IDs in `progress.h` to a message, count type, and format style. `phase_times[8]` stores per-phase and total timing.

## Dependencies

It uses pthreads, POSIX timers/signals, global repair settings such as `glob_agcount`, `ag_stride`, `report_interval`, `verbose`, `no_modify`, and repair logging helpers.

## Risk Areas

- The reporting thread relies on signal/timer behavior and shared globals guarded by `global_msgs.mutex`.
- `PROG_RPT_INC` increments shared counters from worker threads without per-counter locking, so counters are approximate progress telemetry rather than transactional state.
