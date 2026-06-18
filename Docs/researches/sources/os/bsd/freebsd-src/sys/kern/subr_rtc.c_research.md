# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rtc.c

## Purpose

`subr_rtc.c` provides machine-independent helpers for registering and coordinating real-time clock devices. It orders clocks by resolution, reads the best available RTC during boot time initialization, schedules asynchronous writes back to RTC devices, and exposes debug sysctls for one-shot clock I/O.

## Main Data Model

Each registered clock is represented by `struct rtc_instance`:

- `clockdev`: device implementing `CLOCK_GETTIME`/`CLOCK_SETTIME`.
- `resolution`: clock resolution in microseconds.
- `flags`: behavior modifiers such as no-adjust flags.
- `schedns`: optional nanosecond offset for scheduling writes.
- `resadj`: half-resolution adjustment used for coarse clocks.
- `stask`: timeout task used for asynchronous writes.
- `rtc_entries`: list link.

All instances live in `rtc_list`, protected by `rtc_list_lock` (`sx` lock). The list is sorted by increasing resolution value, so more accurate clocks are queried first.

## Registration And Scheduling

`clock_register_flags(clockdev, resolution, flags)` allocates an instance, computes its half-resolution adjustment, initializes its timeout task, inserts it into the sorted list, and logs registration.

`clock_register(dev, res)` registers with no special flags.

`clock_unregister(clockdev)` removes the instance, cancels and drains its pending timeout task, then frees it.

`clock_schedule(clockdev, offsetns)` records a desired nanosecond offset within each second for future RTC writes. `resettodr()` uses this to delay writes until the target offset.

## Reading Time

`read_clocks(ts, debug_read)` iterates registered clocks in resolution order. For each clock it calls `CLOCK_GETTIME`. Invalid negative seconds or nanoseconds are rejected. Unless the clock says no gettime adjustment is needed, it adds `resadj` and `utc_offset()`.

For normal boot reads, the function stops at the first successful clock and optionally logs the provider. For debug reads, it continues to exercise all registered clocks.

`inittodr(base)` initializes system time. It tries `read_clocks()`. If no RTC succeeds, it reports a warning/error and falls back to `base` if positive, otherwise leaves time invalid. Successful reads call `tc_setclock()`, and `ffclock_reset_clock()` when `FFCLOCK` is enabled.

## Writing Time

`resettodr()` writes current system time back to all registered clocks unless `machdep.disable_rtc_set` is set. It does not call drivers directly in the caller’s context. Instead, it enqueues each instance’s timeout task on `taskqueue_thread`, optionally delayed so the write happens near `schedns`.

`settime_task_func()` runs in taskqueue context. Unless `CLOCKF_SETTIME_NO_TS` is set, it reads current time, subtracts `utc_offset()`, optionally adds `resadj`, then invokes `CLOCK_SETTIME`. Errors are logged only when `bootverbose`.

## Debugging

The `debug.clock_show_io` sysctl controls printing of RTC I/O:

- `1`: reads.
- `2`: writes.
- `3`: both.

`clock_dbgprint_bcd()`, `clock_dbgprint_ct()`, `clock_dbgprint_err()`, and `clock_dbgprint_ts()` are helper functions for drivers to log formatted clock values.

The `debug.clock_do_io` sysctl triggers one-shot I/O:

- `1`: read all clocks and discard results.
- `2`: schedule writes via `resettodr()`.

## Dependencies

The file depends on clock device interface methods from `clock_if.h`, taskqueues, `sx` locks, timecounter APIs, optional `FFCLOCK`, sysctl, and bus/device infrastructure.

## Maintenance Notes

Clock driver callbacks are intentionally invoked without holding `rtc_list_lock`, through taskqueue or controlled list traversal, so drivers can sleep or take their own locks. The sorted-list invariant matters because the first successful read becomes the system time source.

The half-resolution adjustment is an intentional policy for whole-second or coarse clocks. Any change to adjustment flags must consider both read and write paths to avoid systematic skew.
