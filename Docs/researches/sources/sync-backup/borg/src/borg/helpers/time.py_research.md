# sources/sync-backup/borg/src/borg/helpers/time.py

## Purpose
Parses, clamps, formats, and computes timestamps for archive metadata, CLI arguments, JSON output, and relative time filters.

## Important APIs, Types, And Functions
`parse_timestamp`, `parse_local_timestamp`, `utcfromtimestampns`, `timestamp`, `safe_s`, `safe_ns`, `safe_timestamp`, `format_time`, `format_timedelta`, `calculate_relative_offset`, `offset_n_months`, `OutputTimestamp`, and `archive_ts_now`. Constants include `SUPPORT_32BIT_PLATFORMS`, `MAX_NS`, and `MAX_S`.

## Control Flow
Timestamp parsing assumes UTC for naive ISO strings in `parse_timestamp`, but local time for CLI `timestamp` parsing if stat fails. Nanosecond timestamps are converted from a UTC epoch without float math. Unsafe negative or too-large timestamps are clamped. Relative offsets parse units `y`, `m`, `w`, `d`, `H`, `M`, and `S`; month offsets preserve day where possible by clamping to the target month length.

## State And Persistence
No mutable state. Constants are computed at import based on 32-bit support policy. `OutputTimestamp` wraps a datetime and serializes in local timezone.

## Dependencies And Integration Points
Used by archive creation/listing, filters, formatters, msgpack timestamp conversion, and JSON output. Depends on filesystem `stat` for file timestamp CLI values.

## Risks And Edge Cases
Local versus UTC assumptions differ by function and must match caller semantics. Year offsets can fail for leap-day or out-of-range dates. Month arithmetic must handle varying month lengths. Clamping future timestamps can hide invalid filesystem metadata but prevents overflow.

## Test Signals
Existing time tests should cover aware/naive parsing, file path timestamp arguments, ns conversion without float precision loss, clamping, output timezone formatting, relative offsets by each unit, month end behavior, and timedelta formatting.
