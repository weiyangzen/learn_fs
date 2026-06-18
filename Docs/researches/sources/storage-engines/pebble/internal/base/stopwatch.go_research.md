# sources/storage-engines/pebble/internal/base/stopwatch.go

Purpose: Provides a small stopwatch abstraction and deterministic testing hook for read duration measurements.

APIs and types: `DeterministicReadDurationForTesting`, `MakeStopwatch`, `deterministicStopwatchForTesting`, `Stop`, and `SlowReadTracingThreshold`.

Control flow and state: The testing hook flips a package-level boolean and returns a cleanup closure. `MakeStopwatch` either captures `time.Now` or returns a deterministic stopwatch. `Stop` returns elapsed time or deterministic duration when enabled.

Persistence and dependencies: Runtime-only timing state. Depends on `time`.

Integration points: Cache read-handle waits and slow read tracing use this to produce metrics/traces that can be made deterministic in tests.

Risks: The package-level testing flag is not concurrency-isolated; tests must use cleanup correctly.

Test signals: No direct test in this subset, but cache/read tests use deterministic timing hooks.
