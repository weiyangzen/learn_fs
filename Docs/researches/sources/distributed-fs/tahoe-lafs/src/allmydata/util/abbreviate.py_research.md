# sources/distributed-fs/tahoe-lafs/src/allmydata/util/abbreviate.py

## Purpose

This module formats durations and byte counts for user-facing status messages and parses compact size strings back into integer byte counts. It is presentation-oriented but participates in configuration and status surfaces where readability matters.

## APIs and control flow

`abbreviate_time()` accepts seconds or `datetime.timedelta`. `None` becomes `"unknown"`, timedeltas get `" ago"` or `" in the future"` suffixes, and thresholds choose seconds, minutes, hours, days, months, or years. `abbreviate_space()` formats bytes using either SI powers of 1000 or IEC powers of 1024 while preserving the historical `kB`/`kiB` style. `abbreviate_space_both()` returns both variants. `parse_abbreviated_size()` accepts integer strings with optional `K/M/G/T/P/E`, optional `I`, and optional `B`, returning `None` for empty input.

## State, dependencies, risks, and tests

There is no persistent state. Dependencies are only `re` and `datetime.timedelta`. The implementation floors quantities with `int()` and treats months as 30 days and years as 365 days, so the output is approximate. `parse_abbreviated_size()` intentionally rejects decimals and silently uppercases suffixes.

Risks are boundary regressions around thresholds such as 119/120 seconds, SI versus IEC suffix confusion, and callers assuming calendar-accurate months. Test signals should cover `None`, timedeltas of both signs, threshold changes, all size suffixes, lowercase parsing, invalid strings, and large values.
