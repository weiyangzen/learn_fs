# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_tc.c

Read status: complete file reviewed.

This file implements FreeBSD's timecounter/timehands core: lockless time reads, timecounter registration and selection, boot time tracking, clock stepping, NTP windup, optional feed-forward clocks, PPS timestamping, CPU tick calibration, and VDSO timehand export.

The main feedback-clock state is `struct timehands`, a ring of cached counter-derived times guarded by generation numbers. `timehands` points to the active entry, `timecounter` points to selected hardware, and `timecounters` is the registered list protected by `tc_lock`. Early boot uses a dummy timecounter so time APIs work before hardware counters register.

Read APIs such as `binuptime`, `nanouptime`, `microtime`, `getnanotime`, and `getboottimebin` snapshot a timehand, read a counter delta with `tc_delta`, and retry if the generation changed. The `get*` variants use cached tick values, while precise variants add current counter deltas. DTrace-specific clones avoid FBT probe recursion.

`tc_init` validates new counters, creates per-counter sysctl nodes, inserts them into the global list, and automatically selects the best nonnegative-quality counter unless a user/tunable choice is active. Sysctls expose `kern.boottime`, available choices, selected hardware, tick/deviation precision, step warnings, timehand count, and fast VDSO gettime enablement.

`tc_setclock` steps wall time by recalculating boot time, winding up timehands under `tc_setclock_mtx`, bumping `rtc_generation`, notifying timerfd, waking sleeps tied to old realtime, and optionally logging the step. `tc_windup` advances the next timehand, processes NTP seconds/leap adjustments, recalculates scaling, switches counters when requested, updates `time_second/time_uptime`, and pushes VDSO state.

When `FFCLOCK` is enabled, the file maintains a separate feed-forward timehands ring (`fftimehands`) with daemon-supplied estimates, interpolation periods, boot time, and status. It implements reset, delta conversion, windup, counter-change handling, last-tick snapshots, absolute/difference conversion, raw counter reads, and `sysclock_getsnapshot`/`sysclock_snap2bintime` integration for comparing feedback and feed-forward clocks.

The PPS section implements RFC 2783 support: `pps_ioctl`, `pps_init`, `pps_init_abi`, `pps_capture`, and `pps_event`. It supports parameter/capability/fetch ioctls, optional feed-forward counter fetches, optional hardpps binding, sleeping fetches, ABI-aware driver locking, assert/clear timestamp capture, offsets, sequence counters, and wakeups.

Periodic maintenance is driven by `tc_ticktock`, which calls `tc_windup` every `tc_tick` hardclock ticks. Initialization sets tick thresholds and timehand ring length. CPU tick support provides a fallback `cpu_ticks` based on the active timecounter, calibrates variable CPU tick rates, and converts ticks to microseconds.

VDSO support fills native and 32-bit `vdso_timehands` with scale, offset count, counter mask, uptime, boot time, and counter-specific data when enabled. DDB support can print the active counter and timehand fields.

Risk areas are generation/fence correctness in lockless readers, overflow in counter-delta scaling, timecounter switch discontinuities, NTP/leap-second update ordering, realtime step wakeups via `rtc_generation`, feed-forward daemon estimate races, PPS capture when counters change, and unsynchronized VDSO publication.
