# File Research: sources/os/bsd/netbsd-src/lib/libutil/parsedate.y

## Purpose
Yacc grammar and lexer for parsing human-readable date/time expressions into `time_t`.

## Key Details
- Supports absolute dates, times, time zones, weekday expressions, relative units, CVS timestamps, epoch `@number`, and ISO-like timestamps.
- Handles time zones via named tables, numeric offsets, daylight variants, and military zones.
- Relative units include seconds, minutes, hours, days, weeks, fortnights, months, and years.
- `parsedate` initializes defaults from either current time or supplied `now`/zone.
- Special pre-parser handles ISO timestamp forms where `T` would confuse the lexer.
- Date conversion validates normalized `struct tm` output to reject invalid dates.
- Relative month handling clamps day-of-month to the target month’s valid last day.
- Overflow checks appear in relative value, weekday, month, and year handling.
- Optional `TEST` main provides interactive parser testing.

## Dependencies and Role
- General date parsing utility used by userland tools.
- Compatibility wrapper `compat_parsedate.c` adapts this implementation to old 32-bit time ABI.
