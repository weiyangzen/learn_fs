# File Research: sources/virtualization/open-iscsi/usr/iscsi_timer.c

## Purpose
`iscsi_timer.c` provides minimal wall-clock timer helpers built on `struct timeval` and `gettimeofday()`.

## APIs
- `iscsi_timer_clear()` zeroes a timer, making it inactive.
- `iscsi_timer_set()` sets a timer to now plus a number of seconds.
- `iscsi_timer_expired()` returns true if a nonzero timer is at or before the current time; null or zero timers never expire.
- `iscsi_timer_msecs_until()` returns milliseconds until expiration, `0` for already expired timers, and `-1` for null or zero/inactive timers. It rounds microseconds to milliseconds with `(partial + 500) / 1000`.

## Integration Notes
The helper is generic and independent of open-iscsi record types. It is used where code needs poll/select-style timeout values derived from simple absolute timers.

## Risk Notes
The implementation uses wall-clock time rather than monotonic time, so system clock changes can affect timeout behavior. The millisecond return type is `int`, which is adequate for the short timers used by this codebase but not a general long-duration timer abstraction.
