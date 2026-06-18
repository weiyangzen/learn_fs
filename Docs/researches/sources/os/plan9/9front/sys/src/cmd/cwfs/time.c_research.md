# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/time.c

Purpose: Time helpers and time formatting for cwfs.

Key behavior:
- `toytime()` returns `time(nil)`.
- `datestr()` formats a `Timet` as `YYYYMMDD`.
- `prdate()` prints current time using cwfs `%T`.
- `Tfmt()` formats `Timet` values as `Day Mon DD HH:MM:SS YYYY`, with `"The Epoch"` for zero.
- `nextime()` computes the next time after `t` matching an hour and not excluded by a weekday bitmask; used for automatic dump scheduling.
- `delay()` wraps `sleep()` in milliseconds.

Notable details:
- The formatter manually fills a fixed string template with day/month names and two-digit fields.
- `nextime()` includes DST/hour-adjustment handling by rechecking the resulting local hour.
