# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/TimeDurationUtil.java

## Purpose
Utility for parsing string time durations with suffixes and converting them to `Duration` or long values in caller-requested units.

## Important APIs, Types, And Functions
Public APIs are `getTimeDurationHelper(name, value, unit)` and `getDuration(name, value, unit)`. Inner enum `ParsedTimeDuration` maps ns, us, ms, s, m, h, and d suffixes to `TimeUnit` and `ChronoUnit`.

## Control Flow
Parsing trims/lowercases the input, detects the suffix by enum order, strips it, parses the numeric portion as a long, and builds a `Duration`. If no suffix is present, it logs a warning and uses the provided default unit.

## State And Persistence
No persistent state beyond logger. Returned values are derived from strings.

## Dependencies And Integration Points
Used by `ConfigurationSource`, `ConfigurationTarget`, and `ConfigType.TIME`.

## Risks
`getTimeDurationHelper` converts through milliseconds, so sub-millisecond durations can be truncated when returning long values. Negative values are not rejected. Blank or non-numeric strings fail at parse time.

## Test Signals
Tests should cover all suffixes, no-suffix default unit behavior, uppercase input, sub-millisecond truncation, negative durations, and invalid strings.
