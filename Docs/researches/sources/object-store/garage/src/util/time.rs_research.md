<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/time.rs -->
# sources/object-store/garage/src/util/time.rs

## Purpose
Timestamp and logical-clock helpers for Garage metadata.

## Important APIs, types, and functions
`now_msec`, `increment_logical_clock`, `increment_logical_clock_2`, and `msec_to_rfc3339`.

## Control flow
Current time is read from `SystemTime` in milliseconds. Logical clocks choose max of wall time and previous timestamp(s)+1. RFC3339 formatting splits milliseconds into seconds/nanoseconds and uses UTC.

## State and persistence behavior
Timestamps generated here are persisted in LWW metadata and logs. They bridge wall-clock time and monotonic update ordering.

## Dependencies and integration points
Used by CRDT LWW wrappers, worker error timestamps, and display/reporting code. Depends on chrono and system clock.

## Risks and test signals
`now_msec` panics if the system clock is before Unix epoch. Overflow on `prev + 1` is theoretically possible. Tests should cover formatting and logical increment behavior under older/newer wall time.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/time.rs -->
