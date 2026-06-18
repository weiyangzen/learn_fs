# sources/distributed-fs/tahoe-lafs/src/allmydata/util/time_format.py

## Purpose

This module formats and parses UTC timestamps, dates, durations, and elapsed deltas for Tahoe CLI/status output. It provides a small accepted duration grammar backed by an enum of unit spellings.

## APIs and control flow

`format_time()` uses `strftime`. `iso_utc_date()` and `iso_utc()` use an optional timestamp or injected clock and return UTC ISO strings with configurable separator. `iso_utc_time_to_seconds()` parses `YYYY-MM-DD[T_ ]HH:MM:SS[.subsec]` and converts with `calendar.timegm`. `parse_duration()` builds a regex from `ParseDurationUnitFormat`, accepts integer counts plus units, and maps seconds, days, 31-day months, and 365-day years to seconds. `parse_date()` parses UTC midnight. `format_delta()` renders elapsed time or `N/A`/`-`.

## State, dependencies, risks, and tests

There is no state. Dependencies are `calendar`, `datetime`, `re`, `time`, `Enum`, and typing. Integration includes config/CLI duration parsing and status timestamps.

Risks include fixed 31-day months, no fractional durations, regex values depending on enum order, local ambiguity in `format_time()` because it formats a passed time tuple, and strict timestamp parsing. Test signals should cover timestamp separators, subseconds, invalid timestamps, each duration unit and case-insensitivity, invalid units, future/None deltas, and date parsing at UTC midnight.
