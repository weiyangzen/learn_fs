# sources/test-tools/stress-ng/stress-timerfd.c

## Purpose
Implements the `timerfd` stressor, which opens many Linux timerfd file descriptors, arms them at a configured rate, waits for expirations through `poll()` or `select()`, reads expiration counters, and probes invalid timerfd operations.

## Important APIs, Types, And Functions
Options include `timerfd-fds`, `timerfd-freq`, and `timerfd-rand`. `stress_timerfd_clockids[]` selects from realtime, monotonic, and boottime clocks where available. `stress_timerfd_set()` builds a nonzero interval with optional jitter. The main `stress_timerfd()` function owns allocation of timerfd arrays, optional `pollfd` arrays, temporary non-timer file fd, timer creation, arming, readiness waiting, invalid syscall probes, fdinfo reads, and cleanup.

## Control Flow
The stressor resolves settings, computes `rate_ns`, creates a temporary directory and unlinked regular file for bad-fd timerfd probes, allocates fd arrays, and creates up to the configured number of timerfds. Non-realtime clock creation falls back to realtime if unsupported. It optionally probes `CLOCK_REALTIME_ALARM` without `CAP_WAKE_ALARM`, waits at the barrier, exercises `timerfd_create()` with invalid flags, and arms every valid timerfd. During the run it either builds an `fd_set` and calls `select()` or builds a compact `pollfd` array and calls `poll()`. Readable timerfds are read for their 64-bit expiration count, optionally queried with `timerfd_gettime()`, optionally re-armed in random mode, and counted as bogo ops.

## State And Persistence Behavior
Runtime state is limited to timerfd descriptors, one regular file descriptor, heap arrays, and a temporary directory. The temp file is unlinked immediately. All valid descriptors are closed and the directory is removed on exit. Timer intervals are kernel fd state only.

## Dependencies And Integration Points
The implemented path requires `sys/timerfd.h`, timerfd create/gettime/settime, and either `poll()` or `select()`. It uses stress-ng capability checks, bad fd generation, fdinfo reads, temp-file helpers, settings, metrics through bogo ops, and proc-state transitions. Metadata is `CLASS_INTERRUPT | CLASS_OS` and `VERIFY_ALWAYS`.

## Risks And Test Signals
Large fd counts can hit `EMFILE`, `ENFILE`, `ENOMEM`, or `FD_SETSIZE` limits. In `select` mode the code avoids fds beyond `FD_SETSIZE`; in `poll` mode it can scale higher but allocates more memory. Invalid gettime/settime calls against a bad fd and regular file fd are deliberately ignored. Test signals are successful creation of at least one timerfd, bogo increments from readable events, fdinfo exercise every `COUNT_MAX` loops, clean closure of all fds, and unimplemented registration when timerfd support is missing.
