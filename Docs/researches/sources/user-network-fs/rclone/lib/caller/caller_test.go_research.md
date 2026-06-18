# sources/user-network-fs/rclone/lib/caller/caller_test.go

## Purpose
This file validates and benchmarks `caller.Present`.

## Important APIs, types, and functions
- `TestPresent` checks negative lookup, immediate-caller skipping, and successful detection of a higher frame.
- `BenchmarkPresent` measures a shallow miss.
- `BenchmarkPresent100` measures a miss under 100 recursive stack frames.

## Control flow
The unit test calls `Present` directly and from an anonymous nested function. The recursive benchmark builds a deep stack once, then loops calls to `Present("NotFound")` from that depth.

## State and persistence behavior
No persistent state is used.

## Dependencies and integration points
The tests use `testing` and `testify/assert`. They directly exercise `caller.go`.

## Risks and edge cases
Benchmarks only cover misses, not successful early or late matches. The unit test does not cover suffix collision behavior or stacks deeper than the 48-frame capture limit.

## Test signals
The direct false result for `"TestPresent"` documents that `Present` skips its immediate caller; the nested true result documents intended higher-stack detection.
