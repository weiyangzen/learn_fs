# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/time.c

Time formatting, dump scheduling time computation, and delay wrapper.

Key responsibilities:
- `toytime()` returns `time(nil)`.
- `datestr()` formats a timestamp as `yyyymmdd`.
- `prdate()` prints current time with `%T`.
- `Tfmt()` formats `Timet` into Plan 9-style textual time.
- `nextime()` computes the next timestamp after `t` at a target hour and not on excluded weekdays.
- `delay()` wraps `sleep()` in milliseconds.

Research notes:
- `Tfmt()` prints `The Epoch` for zero time.
- `nextime()` includes adjustment logic for localtime/DST hour anomalies.
