# sources/storage-engines/pebble/internal/testutils/duration.go

## Purpose
This file provides a test assertion helper for durations while accounting for coarse Windows timer precision.

## Important APIs, Types, and Functions
`DurationIsAtLeast(t, d, minValue)` marks itself as a helper, skips strict checking on Windows when the minimum is below 10ms, and otherwise asserts `d >= minValue` with `require.GreaterOrEqual`.

## Control Flow and State
The function is stateless. It has one platform-specific early return and one assertion path.

## Dependencies and Integration
It depends on `runtime`, `testing`, `time`, and `testify/require`. It is meant for tests that measure sleeps, waits, or rate-limited operations.

## Risks and Edge Cases
The Windows special case can mask short-duration regressions on that platform, but avoids flakes from timer granularity. It does not check upper bounds.

## Test Signals
No direct tests are included. The helper's behavior is normally validated indirectly by tests that would otherwise be flaky.
