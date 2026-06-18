<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts.go -->
## sources/object-store/minio/cmd/dynamic-timeouts.go

Purpose: This file implements an adaptive timeout helper that increases timeouts when recent operations often fail by timeout and decreases timeouts when recent successful durations are well below the current timeout. It is designed for concurrent use by callers recording operation outcomes.

Important APIs and types: Constants define thresholds and limits: failure rate above 33% increases the timeout, failure rate below 10% allows decrease, the adjustment window is 16 entries, and the maximum timeout is 24 hours. `dynamicTimeout` stores the current timeout and minimum as atomics, a fixed-size duration log, a mutex, and an optional retry interval. `dynamicTimeoutOpts` feeds `newDynamicTimeoutWithOpts`. Public methods include `Timeout()`, `RetryInterval()`, `LogSuccess(duration)`, and `LogFailure()`.

Control flow: Construction panics on non-positive timeout/minimum and clamps minimum down to timeout if needed. Each success or failure calls `logEntry`; failures are recorded as `maxDuration`, while negative success durations are ignored. `logEntry` atomically increments the entry count, writes entries into the fixed array under a mutex, and when the 16th entry arrives copies the array, resets the count to zero, releases the mutex, and calls `adjust`. `adjust` counts failures and the maximum successful duration. If the failure percentage exceeds the upper threshold, timeout grows by 25% up to `maxDynamicTimeout` and not below minimum. If failure percentage is below the lower threshold, the max success duration is padded by 25%, and the timeout moves halfway toward that target but not below minimum.

State and persistence behavior: State is in-memory only. Timeout and entry count use atomic int64 values; the log buffer is protected by a mutex. The comment notes entries may be leaked while copying, meaning some concurrent events can be dropped around adjustment boundaries rather than blocking heavily.

Dependencies and integration points: The file depends on `math`, `sync`, `sync/atomic`, and `time`. It is a generic helper used by MinIO components that need adaptive operation deadlines or retry intervals.

Risks: The adaptive algorithm is intentionally lossy under concurrency; callers should not treat every logged outcome as guaranteed input. Threshold boundaries are strict (`>` for increase, `<` for decrease), so exactly 33% or 10% failure rates do not adjust in that direction. A sequence of very fast successes can drive the timeout down to minimum, which may be too aggressive if the workload is bursty. `RetryInterval` is just stored configuration; this type does not enforce sleeps or retries.

Test signals: `dynamic-timeouts_test.go` covers increases, repeated increases, decreases, repeated decreases, convergence above success duration, minimum clamping, concurrent logging under race-style pressure, and random exponential/normal duration distributions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts.go -->
