# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_time_format.py

## Purpose

This file tests `allmydata.util.time_format`, covering UTC ISO formatting/parsing, duration/date parsing, stable struct-time formatting, Y2038-adjacent behavior, and human-readable delta formatting. It protects Tahoe code that displays crawler/operator times, parses lease durations or dates, and needs timezone-stable UTC conversions.

## Important APIs, Types, and Helpers

`TimeFormat` inherits from Twisted Trial `TestCase` and `.common_util.TimezoneMixin`. `TimezoneMixin` supplies `have_working_tzset` and `setTimezone` so timezone-sensitive behavior can be tested without permanently changing process state.

The tested APIs are `iso_utc_time_to_seconds`, `iso_utc`, `iso_utc_date`, `parse_duration`, `parse_date`, `format_time`, and `format_delta`.

`_help_test_epoch` is shared by default timezone and Europe/London timezone tests. It captures `time.tzname`, performs conversions, and asserts the original timezone name is restored.

## Control Flow

`test_epoch` and `test_epoch_in_London` verify that ISO UTC strings around the Unix epoch convert to absolute seconds regardless of local timezone oddities. The London test is conditional on working `time.tzset()` because Europe/London had a GMT+1 standard-time offset in 1970.

`_help_test_epoch` accepts `T`, underscore, and space separators, validates `iso_utc` output with underscore and custom separator, round-trips current time to whole seconds, accepts a callable `t=` provider, rejects incomplete ISO strings with `ValueError`, parses fractional seconds, and checks a 2009 daylight-savings-sensitive timestamp.

`test_iso_utc` checks date-only and full UTC formatting for a fixed fractional timestamp and a custom separator. `test_parse_duration` covers seconds, days, 31-day months, and 365-day years with whitespace/case/plural variations, plus invalid strings. `test_parse_date` checks YYYY-MM-DD parsing to UTC midnight seconds.

`test_format_time` validates formatting of `time.gmtime` results at epoch, minute/hour boundaries, and January 1, 2015 using manually computed leap-year days. `test_format_time_y2038` computes January 1, 2048, skips if the platform cannot represent it, and otherwise checks formatting. `test_format_delta` verifies positive deltas from seconds through multi-day spans, reverse-time `-`, and fractional start times truncating displayed whole seconds.

## State and Persistence Behavior

There is no file persistence. The only mutable state is process timezone environment/state managed through `TimezoneMixin` and `time.tzset` where available. The tests explicitly assert that timezone names are restored after helper execution.

## Dependencies and Integration Points

The file depends on Python `time`, Twisted Trial, Tahoe `TimezoneMixin`, and `allmydata.util.time_format`. These functions are integration points for lease expiration display, status pages, command-line date/duration parsing, and other operator-facing time formatting.

## Risks and Edge Cases

Timezone behavior is platform-dependent, so London epoch testing is skipped if `tzset` support is missing. Y2038/post-2037 behavior is also platform-dependent and skipped on systems whose `time.gmtime` cannot handle 2048.

Duration parsing encodes Tahoe-specific approximations: a month is 31 days and a year is 365 days. Changes to those semantics would require deliberate test updates. `format_delta` floors fractional start times in a way that is visible in expected strings.

## Test Signals

Passing tests signal that UTC parsing/formatting is independent of local timezone, fractional seconds are preserved where expected, date/duration parsers accept documented human forms and reject unitless/unknown units, and display formatting remains stable across boundary dates and negative deltas.
