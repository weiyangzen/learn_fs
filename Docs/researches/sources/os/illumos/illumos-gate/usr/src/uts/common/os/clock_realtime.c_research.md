# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_realtime.c

This file registers the `CLOCK_REALTIME` backend and the compatibility `__CLOCK_REALTIME0` backend. It wraps wall-clock get/set operations and implements realtime POSIX timers on top of timeout callouts.

Core behavior:
- `clock_realtime_settime()` takes `tod_lock`, writes the TOD with `tod_set()`, and resets high-resolution system time via `set_hrestime()`.
- `clock_realtime_gettime()` calls `gethrestime()`, though libc normally uses a faster path for `CLOCK_REALTIME`.
- `clock_realtime_getres()` reports `nsec_per_tick`.
- Timer creation allocates a `timeout_id_t` slot and records the generic `it_fire()` callback.
- `clock_realtime_timer_settime()` removes any existing timeout under `p_lock`, records the new `it_itime`, converts relative times to absolute `hrestime`, and schedules the first fire through `realtime_timeout()`.
- The first fire uses `clock_realtime_fire_first()` to avoid firing early because `timespectohz()` is based on `hrestime` while callouts are interpreted against lbolt.
- `clock_realtime_fire()` invokes the timer subsystem, clears one-shot timers, or computes the next interval expiration by stepping forward from the previous expected expiration. If the clock moved, it uses exponential stepping and then normal stepping to find the minimum future deadline.
- `clock_realtime_timer_gettime()` snapshots `it_itime` and current time under `p_lock`, returning zero remaining time when expired.
- Deletion cancels outstanding timeouts and frees `it_arg`.

Important invariants:
- `p_lock` protects `it_itime` and the active timeout id.
- `untimeout()` is called with the process lock dropped and then reacquired because timeout removal can block.
- Realtime interval timers preserve cadence from the expected expiration time instead of simply adding interval to current time.
- Wall-clock changes can force recomputation of future interval deadlines.
