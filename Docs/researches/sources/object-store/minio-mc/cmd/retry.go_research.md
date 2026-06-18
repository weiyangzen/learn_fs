# sources/object-store/minio-mc/cmd/retry.go

## Purpose
Provides a small reusable retry manager for commands that want bounded retry attempts with jitter and cancellation.

## Important APIs, types, and functions
- `retryManager` tracks attempt count, max retries, interval, parent command context, and a retry-specific cancellation context.
- `newRetryManager` creates a retry context independent of the command context and stores its cancel function.
- `retryMessage` formats retry telemetry for text/JSON output.
- `(*retryManager).retry` repeatedly invokes an action until success, max retries, retry cancellation, or command cancellation.

## Control flow
`retry` defers cancellation of its retry context, then loops while `retries <= maxRetries`. It calls the provided action with the manager. A nil error returns immediately. On error it waits for either retry cancellation, parent command cancellation, or a randomized delay between half the retry interval and roughly 1.5x the retry interval, then increments the retry count.

## State and persistence
In-memory only. The manager mutates `retries` and context state. It does not persist attempt data.

## Dependencies and integration points
Uses Go `context`, `time`, `math/rand`, `probe.Error`, color JSON output, and global `fatalIf` for JSON marshalling errors.

## Risks and edge cases
- Loop condition `<= maxRetries` means the action can run `maxRetries + 1` times.
- Uses the package-level `math/rand` source without explicit seeding here; jitter may be deterministic depending on process setup.
- `retryCtx` is based on `context.Background`, so only explicit `cancelRetry` or parent `commandCtx` stops it.

## Test signals
No direct tests. Useful tests would assert attempt counts, cancellation by command context, cancellation by retry context, and jitter path behavior with very small intervals.
