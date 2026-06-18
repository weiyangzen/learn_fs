# File Research: sources/os/bsd/netbsd-src/sys/sys/clock.h

## Scope

Defines basic calendrical constants and inline helpers.

## APIs And Behavior

- Constants for seconds per minute/hour/day, days per common/leap year, seconds per common/leap year, and `POSIX_BASE_YEAR`.
- `days_in_month(m)` returns month length for 1-12, assuming February has 28 days, or `-1` for invalid months.
- `is_leap_year(year)` implements Gregorian leap-year logic with branch prediction hints.
- `days_per_year(year)` returns 365 or 366.

## Dependencies

- Userland/standalone distinction controls inclusion of `stdint.h`.

## Risks And Invariants

- `days_in_month` does not account for leap years; callers must add February adjustment separately.
- Year type is `uint64_t`.
