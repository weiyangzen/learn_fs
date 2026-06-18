# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ffclock.c

Read status: complete file reviewed.

This file implements the optional feed-forward clock syscall and high-level time access layer when `FFCLOCK` is enabled, with ENOSYS stubs otherwise. It exposes absolute time, uptime, interval conversion, sysclock selection sysctls, and user/kernel estimate exchange.

Main functions under `FFCLOCK` include `ffclock_abstime`, `ffclock_difftime`, the `ffclock_*time` and `ffclock_*uptime` wrapper family, `ffclock_*difftime` wrappers, `sys_ffclock_getcounter`, `sys_ffclock_setestimate`, and `sys_ffclock_getestimate`.

`ffclock_abstime` reads the feed-forward counter, either through the fast last-tick path or direct counter read plus conversion, then snapshots `ffclock_estimate` using `update_ffcount` as a generation check. It applies optional leap-second adjustment, optional boot-time subtraction for uptime clocks, and optional error-bound calculation based on elapsed counter time, absolute error, and rate error. `ffclock_difftime` converts a counter delta to bintime and optionally computes interval error bounds from the current estimate's rate error.

The sysctl tree adds `kern.sysclock`, `kern.sysclock.ffclock`, `kern.sysclock.available`, `kern.sysclock.active`, `kern.sysclock.ffclock.version`, and `kern.sysclock.ffclock.ffcounter_bypass`. The active sysclock handler exposes `"feedback"` and `"feed-forward"` and allows switching `sysclock_active` by string.

The wrapper functions provide standard FreeBSD clock APIs backed by ffclock: wall-clock bintime/nanotime/microtime, fast get* variants, uptime variants with `FFCLOCK_UPTIME`, and difference conversions from `ffcounter` deltas. They compose flags such as `FFCLOCK_LERP`, `FFCLOCK_LEAPSEC`, `FFCLOCK_FAST`, and `FFCLOCK_UPTIME`.

Syscalls support userland synchronization daemons and applications. `sys_ffclock_getcounter` returns the current counter or EAGAIN if unavailable. `sys_ffclock_setestimate` requires `PRIV_CLOCK_SETTIME`, copies in an estimate, updates global `ffclock_estimate` under `ffclock_mtx`, and increments `ffclock_updated` so timehands pick up the new estimate. `sys_ffclock_getestimate` copies out the current estimate under the same mutex.

When `FFCLOCK` is not compiled in, the three syscalls return `ENOSYS`, preserving syscall symbols without enabling functionality.

Risk areas are lockless estimate snapshot consistency, generation wrap assumptions, precision/overflow in fixed-point error-bound multipliers, sysclock string matching, privilege enforcement for estimate updates, and behavior when hardware counter reads return zero.
