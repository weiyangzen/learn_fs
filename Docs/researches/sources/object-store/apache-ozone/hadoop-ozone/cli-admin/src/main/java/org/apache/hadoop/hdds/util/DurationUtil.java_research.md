# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/DurationUtil.java

## Purpose
Provides a small utility for formatting `Duration` values as compact human-readable strings.

## Important APIs, Types, And Functions
`DurationUtil` is final with a private constructor. `getPrettyDuration(Duration)` returns strings like `1h 30m 45s`, `2m 30s`, or `30s` based on whole seconds.

## Control Flow
The method calculates hours, minutes, and seconds from `duration.getSeconds()`. It prefers hours output, then minutes output, then non-negative seconds, otherwise throws `IllegalStateException`.

## State And Persistence
Stateless and pure for non-negative durations.

## Dependencies And Integration Points
Depends only on `java.time.Duration` and `String.format`. It is available to CLI code needing duration display.

## Risks And Test Signals
Negative durations throw only when seconds is negative; nanosecond-only negative edge cases should be considered. Tests should cover zero, sub-minute, minute, hour, multi-hour, and negative durations.
