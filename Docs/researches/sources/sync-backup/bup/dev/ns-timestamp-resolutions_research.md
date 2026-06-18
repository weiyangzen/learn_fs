# sources/sync-backup/bup/dev/ns-timestamp-resolutions

## Purpose
Measures apparent nanosecond timestamp resolution for atime and mtime on a target filesystem.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses bup `options`, `metadata.from_path`, `xstat.utime`, `argv_bytes`, and `saved_errors`.

## Control Flow
Parses one test filename, creates it, sets atime/mtime to `123456789` ns, reads metadata, computes trailing-zero decimal resolution for both timestamps, and prints two integers.

## State and Persistence Behavior
Creates/modifies the supplied test file. Reads bup metadata timestamps.

## Dependencies and Integration Points
Used by tests needing filesystem timestamp granularity.

## Risks and Test Signals
Risks include typo/undefined `log` in saved-error branch, filesystem rounding, and platform utime semantics. Signal is `atime_resolution mtime_resolution` output.
