# sources/test-tools/fio/steadystate.c

## Purpose
`steadystate.c` implements fio's steady-state termination logic. It tracks bandwidth, IOPS, and latency over a configured duration and ends jobs when either a slope criterion or maximum-deviation criterion falls below the configured limit.

## Important APIs, Types, And Functions
Public functions are `steadystate_free()`, `steadystate_setup()`, `steadystate_check()`, `td_steadystate_init()`, `steadystate_bw_mean()`, `steadystate_iops_mean()`, and `steadystate_lat_mean()`. Globals are `steadystate_enabled` and `ss_check_interval`. Internal algorithms are `steadystate_slope()` and `steadystate_deviation()`, both of which update ring buffers and criteria in `struct steadystate_data`.

## Control Flow
`td_steadystate_init()` translates job options into per-thread steady-state fields, converts duration/check interval units, initializes regression sums, sets ramp-over state if no ramp time exists, and rejects inconsistent options inside a reporting group. After all jobs are initialized, `steadystate_setup()` allocates ring buffers either per job or on the last thread in each group-reporting group. Periodic `steadystate_check()` skips inactive/exited/attained jobs, computes deltas since the previous check, aggregates group values, waits for ramp time, applies slope or deviation logic, marks `FIO_SS_ATTAINED`, and asks fio to terminate affected threads.

## State And Persistence Behavior
Each `thread_data` owns a `steadystate_data` with ring buffers, head/tail indexes, previous I/O counters, prior latency sums, regression sums, and final criterion values. In group-reporting mode, only one thread per group stores data (`FIO_SS_DATA`), while attainment is propagated to every thread in the group. State is in-memory only but copied into `thread_stat` for final reports.

## Dependencies And Integration Points
The file depends on `fio.h`, `steadystate.h`, thread iteration macros, async I/O locks, `fio_gettime()`, `fio_mark_td_terminate()`, and stat fields for completion latency means/samples. `stat.c` uses the exported mean helpers and report fields to render steady-state output.

## Risks And Edge Cases
Interval count is computed by dividing duration by `ss_check_interval / 1000L`; invalid small intervals or durations can produce zero or divide-by-zero risks if option validation elsewhere fails. Allocation failures in `steadystate_alloc()` are not checked before setting `FIO_SS_DATA`. Slope calculations assume equally spaced x-values even though comments admit real intervals may drift. Group aggregation depends on thread iteration order by group id. Latency uses completion-latency mean deltas, so jobs with no latency samples get zero group latency.

## Test Signals
Tests should cover slope and deviation attainment, percent and absolute criteria, ramp-time delay, group-reporting propagation, inconsistent group option rejection, zero/short duration validation, allocation failure behavior, and final report ring ordering after wraparound.
