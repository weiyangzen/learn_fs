# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_clock.c

## Purpose
Provides generic kernel conversions between POSIX `timespec`, binary `clocktime`, and BCD RTC clock formats, plus clock debugging and UTC-offset sysctl support.

## Main Elements
- Sysctls:
  - `machdep.adjkerntz`: local UTC offset in seconds; writes call `resettodr()`.
  - `debug.clocktime`: enables conversion debug printing.
  - `machdep.wall_cmos_clock`: controls whether `utc_offset()` returns `adjkerntz`.
- Calendar helpers:
  - Leap-year, days-per-month/year, day-of-week, and a precomputed 2017 day-count base for faster conversions.
  - `nsdivisors[]` supports fractional-second printing with 0-9 digits.
- Conversion APIs:
  - `clock_ct_to_ts()` converts `struct clocktime` to `timespec`, including 2-digit RTC year pivoting.
  - `clock_bcd_to_ts()` validates BCD fields, converts to binary, handles optional AM/PM mode, then calls `clock_ct_to_ts()`.
  - `clock_ts_to_ct()` converts seconds since 1970 to calendar fields and weekday.
  - `clock_ts_to_bcd()` converts `timespec` to BCD RTC fields with optional AM/PM mode.
- Printing helpers:
  - `clock_print_bcd()`, `clock_print_ct()`, `clock_print_ts()`.
- `utc_offset()`: returns local offset only when wall CMOS clock mode is enabled.

## Dependencies And Integration
Used by RTC and platform clock drivers through `<sys/clock.h>`. Depends on kernel sysctl, timecounter definitions, BCD macros, and `resettodr()`.

## Risk Notes
`clock_ct_to_ts()` rejects invalid calendar fields and protects 32-bit `time_t` from post-2037 overflow. BCD inputs are validated before conversion to avoid assertions. Leap seconds are not fully modeled: input seconds above 59 are rejected in `clock_ct_to_ts()`, while `clock_ts_to_ct()` permits an asserted range up to 60.
