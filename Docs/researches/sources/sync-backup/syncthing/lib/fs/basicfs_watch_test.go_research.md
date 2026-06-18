# sources/sync-backup/syncthing/lib/fs/basicfs_watch_test.go

## Purpose
Exercises `BasicFilesystem.Watch` end-to-end and at the `watchLoop` level across ignore filtering, event classification, path normalization, overflow, and platform edge cases.

## Important APIs, Types, and Functions
`TestMain` creates a real watched root and shrinks `backendBuffer`. `testScenario`, `testWatchOutput`, `fakeMatcher`, and `fakeEventInfo` drive scenarios. Tests cover ignore/include, rename, Windows root handling, outside-root errors, subpath events, overflow, Linux error interpretation, symlinked roots, Windows case issue 4877, modtime changes, and truncate-only changes.

## Control Flow
Most tests create a watched directory, start `Watch`, mutate files, and wait until expected events cancel the context. Lower-level tests inject fake backend events into `watchLoop` to avoid relying on OS notification timing for path checks.

## State and Persistence Behavior
Uses a shared `testdata` directory under the package working directory, removed before and after the test run. Watch goroutines are canceled via contexts.

## Dependencies and Integration Points
Depends on `notify`, `build` platform flags, `ignoreresult`, and real OS notifications.

## Risks
Timing-based waits can be flaky on loaded systems. Platform-specific notify behavior requires allowed extra events and skips for OpenBSD. Overflow checks depend on intentionally small channel buffering.

## Test Signals
Provides high-value regression coverage for watcher safety: outside-root events become fatal errors, ignored paths are filtered, overflow schedules a broad scan, and symlinked roots do not panic.
