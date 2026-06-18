# sources/test-tools/fio/fio_time.h

Purpose: declares fio's wall-clock, monotonic-clock, ramp-period, sleep/spin, and job epoch timing helpers.

Important APIs/types/functions: declares `ramp_period_enabled`, `RAMP_PERIOD_CHECK_MSEC`, `ntime_since`, `utime_since`, `mtime_since`, `rel_time_since`, `time_since_now`, genesis-time helpers, `cycles_spin`, `usec_spin`, `usec_sleep`, `fill_start_time`, `fio_time_init`, ramp-period helpers, `timespec_add_msec`, and `set_epoch_time`.

Control flow: consumers call initialization and epoch helpers during fio startup/job start, then use elapsed-time helpers throughout rate control, ETA, latency accounting, ramp transitions, and timeouts. Ramp helpers indicate whether stats should still be suppressed or reset.

State and persistence behavior: the header exposes timing API over process-global genesis/ramp state and per-job `thread_data` timing fields. It does not define storage itself except the external ramp-period flag declaration.

Dependencies/integration: includes standard time headers and fio types. It is paired with `gettime.h`/`gettime.c` and used by backend, rate, stats, and synchronization code.

Risks and test signals: mixed nanosecond/microsecond/millisecond units are easy to confuse, and signed versus clamped elapsed functions have different semantics. Test signals should cover negative/warped time, ramp completion, alternate clocks, sleep precision, and arithmetic overflow near large intervals.
