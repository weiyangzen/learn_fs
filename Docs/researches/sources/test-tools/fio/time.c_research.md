# sources/test-tools/fio/time.c

## Purpose
`time.c` implements fio timing helpers, sleep/spin behavior, global genesis time, job epoch fields, and ramp-period state transitions.

## Important APIs, Types, and Functions
`timespec_add_msec()` mutates a timespec by milliseconds. `usec_spin()` and `cycles_spin()` busy-wait for fine-grained timing. `usec_sleep()` combines nanosleep with spin compensation based on measured `ns_granularity`, waking periodically to observe `td->terminate`. `time_since_genesis()`, `mtime_since_genesis()`, and `utime_since_genesis()` report elapsed time from global `genesis`.

Ramp APIs include `in_ramp_period()`, global `ramp_period_enabled`, `ramp_period_check()`, `ramp_period_over()`, and `td_ramp_period_init()`. They support ramp by time or bytes, group-reporting semantics, offload parent/child propagation, and stats reset at ramp completion. `fio_time_init()` initializes clock support and measures nanosleep granularity. `set_genesis_time()`, `set_epoch_time()`, and `fill_start_time()` initialize job timestamps.

## Control Flow and State
File-static state includes `genesis` and `ns_granularity`. Ramp state lives in each `thread_data.ramp_period_state` and global `ramp_period_enabled`. `ramp_period_check()` iterates all thread data, optionally locks async workers while reading I/O bytes, and marks jobs/groups finishing.

## Dependencies and Integration Points
It depends on `fio.h`, clock helpers, thread iteration macros, thread runstate transitions, stats reset functions, and async locking. It affects runtime accounting, logs, ETA, ramp exclusion, and job start epoch output.

## Risks and Test Signals
Risks include busy-spin CPU burn, nanosleep granularity over/under-compensation, group byte accounting depending on thread iteration order, and ramp-size consistency enforcement. Signals include ramp-time/ramp-size tests, stable job_start/alternate_epoch log fields, and absence of hangs during termination.
