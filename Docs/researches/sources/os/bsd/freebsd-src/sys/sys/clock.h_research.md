# File Research: sources/os/bsd/freebsd-src/sys/sys/clock.h

## Purpose
Declares kernel-only calendrical and time-of-day clock services for RTC drivers, timezone/localtime conversions, BCD conversion, FAT timestamp conversion, and clock registration.

## Main Elements
- `struct clocktime` stores binary calendar fields and nanoseconds.
- `struct bcd_clocktime` stores BCD calendar fields plus AM/PM state.
- Conversion APIs: `clock_ct_to_ts()`, `clock_ts_to_ct()`, `clock_bcd_to_ts()`, `clock_ts_to_bcd()`.
- RTC registration APIs: `clock_register()`, `clock_register_flags()`, `clock_schedule()`, `clock_unregister()`.
- Clock flags control whether set/get paths apply timestamps, UTC offset, and resolution/accuracy adjustment.
- FAT helpers: `timespec2fattime()` and `fattime2timespec()`.
- Debug/print helpers for clocktime, BCD clocktime, and timespec values.

## Dependencies And Integration
Only exposes content under `_KERNEL`. Used by RTC and filesystem code that must translate hardware/local calendar formats into kernel timespecs.

## Risk Notes
Year interpretation is deliberately nuanced for two-digit RTCs, century-bit hardware, and full years. Incorrect use can produce bad filesystem or RTC timestamps, especially when localtime and UTC offsets differ.
