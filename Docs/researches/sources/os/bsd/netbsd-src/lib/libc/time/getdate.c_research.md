# File Research: sources/os/bsd/netbsd-src/lib/libc/time/getdate.c

## Purpose
Implements POSIX `getdate` using templates from the `DATEMSK` environment variable.

## Key Elements
Validates `DATEMSK`, stats and opens the template file, parses each non-comment logical line with `fparseln`, tries `strptime`, fills unspecified fields from current local time or future matching weekday/month/hour rules, normalizes with `mktime`, and returns a static `struct tm`.

## Dependencies
Uses `getenv`, `stat`, `fopen`, `fparseln`, `strptime`, `time`, `localtime`, `mktime`, and global `getdate_err`.

## Behavior/Risks
Not thread-safe because it uses static result storage and global `getdate_err`. Timezone scanning is intentionally limited to current localtime behavior. One template mismatch path returns without closing the opened file.
