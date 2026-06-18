# File Research: sources/os/bsd/netbsd-src/lib/libc/time/zdump.c

## Purpose
Implements `zdump`, the timezone diagnostic utility that prints current times or transition tables for one or more timezones. It can list verbose transitions, compact transition data, and bounded year/time ranges.

## Command-Line Interface
`main` supports:
- `--version`
- `--help`
- `-c [L,]U`: limit transition output by calendar years, defaulting to `ZDUMP_LO_YEAR` through `ZDUMP_HI_YEAR`.
- `-t [L,]U`: limit transition output by raw seconds since 1970.
- `-i`: experimental brief transition format.
- `-v`: verbose transition listing.
- `-V`: less verbose transition listing.

Without `-i`, `-v`, or `-V`, it prints the current time in each requested zone.

## Timezone Access Strategy
When `localtime_rz` is available, `zdump` uses timezone objects through `tzalloc`, `tzfree`, and `localtime_rz`. Otherwise it falls back to setting `TZ` in the process environment and calling `tzset`/`localtime_r`.

`gmtzinit` creates a GMT timezone object for efficient UTC conversion where supported. `my_gmtime_r` uses that object or falls back to `gmtime_r`.

The fallback `tzalloc` either uses `setenv("TZ", ...)` or manually constructs a temporary environment when `setenv` is unavailable.

## Transition Detection
For verbose modes, `main`:
- Converts year cuts to `time_t` with `yeartot`.
- Starts from the lower bound and samples forward in half-day increments.
- Detects changes in localtime definedness, UTC offset, DST flag, or abbreviation.
- Calls `hunt` to binary-search the exact transition timestamp.
- Prints times around transitions with `show` or compact records with `showtrans`.

`hunt` compares endpoints and repeatedly bisects using `localtime_rz`, abbreviation snapshots, `tm_isdst`, and calendar-time deltas until it finds the transition boundary.

`showextrema` handles transitions into or out of representable local/GMT time near `time_t` extrema.

## Formatting Helpers
- `show`: prints a zone name, UTC time, local time, abbreviation, DST flag, and GMT offset when verbose.
- `dumptime`: prints a `struct tm` in fixed English day/month format.
- `showtrans`: prints compact transition records with custom `istrftime` extensions.
- `istrftime`: wraps `strftime` and adds `%f` for quoted zone name, `%L` for local time, and `%Q` for offset/abbreviation/DST tuple output.
- `format_local_time`, `format_utc_offset`, and `format_quoted_string` implement compact machine-readable pieces.
- `tformat` chooses a printf format for `time_t`.
- `saveabbr` preserves abbreviations across calls on platforms where `tzname` may be overwritten.

## Validation and Warnings
`abbrok` warns once per zone if an abbreviation has non-ASCII-alphanumeric/sign characters, fewer than 3 characters, or more than 6 characters. `TYPECHECK` builds can verify `localtime_rz` round-trips through `mktime_z`.

The program tracks `errout` to report warning/error output failures.

## Range and Overflow Handling
The file computes `absolute_min_time` and `absolute_max_time` from the native `time_t` representation. `yeartot` converts years to `time_t` using 400-year Gregorian cycles where safe and saturates at extrema on overflow. `sumsize`, `xmalloc`, and formatting loops guard dynamic buffer growth.

## Dependencies
Depends on `private.h` for timezone APIs, calendar constants, attributes, integer helpers, gettext hooks, and portability shims. Uses libc APIs including `getopt`, `strtoimax`, `strftime`, `printf`, `setenv`, `tzset`, `localtime_r`, `gmtime_r`, `malloc`, and errno/string helpers.

## Notable Risks and Edge Cases
- Fallback mode mutates process-global `TZ`, so behavior differs from timezone-object mode.
- Transition discovery samples by half-day, then binary-searches; it relies on tzcode’s expectation that relevant observable changes are detectable at that cadence before refinement.
- Output formatting dynamically grows buffers; all growth is guarded but can exit on allocation failure.
- The utility intentionally supports unusual `time_t` ranges and saturates year cuts at representable extrema.
