# File Research: sources/os/bsd/netbsd-src/lib/libc/time/localtime.c

## Purpose
NetBSD’s imported and adapted tzcode implementation for converting between `time_t` and `struct tm`, loading compiled TZif timezone files, parsing POSIX `TZ` strings, maintaining libc timezone globals, and providing NetBSD timezone-object APIs.

It implements the core libc time entry points: `tzset`, `localtime`, `localtime_r`, `gmtime`, `gmtime_r`, `mktime`, `timegm`, `offtime`, `timeoff`, `timelocal`, `time2posix`, `posix2time`, plus NetBSD-inspired `tzalloc`, `tzfree`, `localtime_rz`, `mktime_z`, `time2posix_z`, `posix2time_z`, `tzgetname`, and `tzgetgmtoff`.

## Core Data Structures
- `struct state`: in-memory timezone rule set loaded from TZif or parsed from a POSIX `TZ` string. It stores transition times, transition type indexes, type records, abbreviation bytes, leap-second records when enabled, and `goback`/`goahead` repeat flags.
- `struct ttinfo`: one local-time type, including UTC offset, abbreviation index, DST flag, and standard/UTC transition indicators.
- `struct lsinfo`: leap-second transition and correction.
- `struct rule`: parsed POSIX DST transition rule, supporting Julian day, day-of-year, and month-week-weekday forms.
- Global local/GMT state: `lclptr`/`lclmem`, `gmtptr`/`gmtmem`, cached `lcl_TZname`, `lcl_is_set`, and libc globals `tzname`, `timezone`, `daylight`, and optionally `altzone`.

## Timezone Loading
`tzloadbody` is the main TZif loader. It:
- Resolves `TZDEFAULT`, `TZDIR`, absolute paths, and relative zone names.
- Applies privilege hardening through `issetugid`, rejects unsafe arbitrary absolute paths for privileged callers, guards relative names containing dangerous `..` components, and avoids device side effects where possible.
- Opens zone files with conservative flags such as close-on-exec, no controlling terminal, regular-file hints, and optional `openat`-based `TZDIR` containment.
- Parses v1/v2/v3-style TZif data blocks, validating counts against `TZ_MAX_*` limits.
- Reads 32-bit or 64-bit transition times, transition type indexes, ttinfo records, abbreviation strings, leap-second records, and standard/UTC indicator arrays.
- Discards transitions outside representable `time_t` while preserving boundary behavior.
- Parses a trailing newline-delimited POSIX rule string when present and extends future transitions from it.
- Scrubs invalid abbreviation characters and rejects overlong abbreviations.

`tzload` wraps `tzloadbody` with stack or heap temporary storage. `zoneinit` handles empty `TZ` as UTC-like fast mode, otherwise tries TZif loading and falls back to `tzparse` for POSIX strings.

## POSIX TZ Parsing
The parser helpers `getzname`, `getqzname`, `getnum`, `getsecs`, `getoffset`, `getrule`, and `transtime` parse standard/DST names, offsets, and transition rules. `tzparse` builds a synthetic `struct state`:
- Supports quoted abbreviations with `<...>`.
- Accepts explicit or default DST offsets.
- Uses `TZDEFRULESTRING` when DST exists but no rules are supplied.
- Generates transitions across `years_of_observations` and marks states repeatable with `goback`/`goahead` when safe.
- Reuses leap-second data from a base TZif state when extending a loaded zone.

## Conversion Flow
`timesub` converts a `time_t` plus UTC offset into `struct tm`, accounting for leap seconds, Gregorian 400-year cycles, signed/unsigned `time_t`, weekday/year-day/month-day calculation, `tm_gmtoff`, and leap-second `tm_sec == 60`.

`localsub` selects the applicable `ttinfo` for a timestamp via transition search, handles proleptic repeated rules before/after the explicit transition table, calls `timesub`, sets `tm_isdst`, `tm_zone`, and optionally updates libc globals.

`gmtsub` is the GMT/fixed-offset equivalent. `gmtcheck` lazily initializes the GMT state once via `gmtload`.

## Reverse Conversion
`mktime` and related functions use `time1`, `time2`, and `time2sub`:
- Normalize out-of-range fields in `struct tm`.
- Binary-search the full `time_t` range for a matching broken-down time.
- Retry with normalized seconds to handle leap-second inputs.
- Resolve requested `tm_isdst` by trying alternative offsets from known timezone types.
- Use `tm_gmtoff` heuristics when available and safe.
- Return `EOVERFLOW` or `EINVAL` for unrepresentable or invalid inputs.

`timegm` copies the input and calls `timeoff` with zero offset. `timelocal` forces unknown DST before delegating to `mktime`.

## Threading and NetBSD Integration
When `_REENTRANT` is set, the file enables thread-safe locking, read/write locks, and thread-specific static `struct tm` storage. `lock`, `unlock`, `rd2wrlock`, `is_threaded`, and `get_monotonic_time` are exposed internally as `__lcl_*` symbols for use by related libc files such as `strftime.c`.

`tzset_unlocked` is the shared critical-section implementation. It refreshes timezone state from `TZ`, supports optional periodic TZif change detection, upgrades a read lock to a write lock when needed, updates `tzname`/`timezone`/`daylight`, and falls back to UTC or `-00` on load errors.

## Dependencies
Depends on:
- `private.h` for portability macros, NetBSD feature defaults, `timezone_t`, time constants, attributes, and prototypes.
- `tzfile.h` for TZif wire-format limits and header layout.
- libc/POSIX APIs: `open`, `openat`, `read`, `close`, `stat`, `fstat`, `getenv`, `clock_gettime`, `pthread_*`, `malloc`, `free`, string/memory functions, and errno handling.

## Notable Risks and Edge Cases
- Security-sensitive path handling around `TZ`, `TZDIR`, privileged execution, relative traversal, and device files.
- Overflow-sensitive arithmetic across all `time_t` widths, including unsigned and non-two’s-complement portability cases.
- Leap-second handling changes both forward and reverse conversions.
- `mktime` behavior around DST gaps/folds depends on heuristics and compile-time options.
- Shared global timezone state is protected by internal locking, but compatibility globals remain process-wide.
