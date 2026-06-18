# sources/user-network-fs/rclone/lib/pacer/pacers.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacers.go -->
## sources/user-network-fs/rclone/lib/pacer/pacers.go

Purpose: defines pacing calculators used by rclone's `lib/pacer` package to choose delay durations after successful calls, retryable failures, and explicit retry-after errors. The file contains reusable option types (`MinSleep`, `MaxSleep`, `DecayConstant`, `AttackConstant`, `Burst`) and three concrete calculators: `Default`, `GoogleDrive`, and `S3`, plus `ZeroDelayCalculator` and `AzureIMDS`.

Important APIs and control flow: `NewDefault`, `NewGoogleDrive`, `NewS3`, and `NewAzureIMDS` construct calculators with defaults and apply typed options. Each calculator implements `Calculate(state State) time.Duration`, consuming `State.SleepTime`, `State.ConsecutiveRetries`, and `State.LastError`. `Default` uses retry-after when present, exponential attack on retries, and decayed sleep on success. `GoogleDrive` adds a `rate.Limiter` for successful calls and randomized truncated exponential backoff for retries. `S3` allows zero delay during healthy operation while using `minSleep`/`maxSleep` on failures. `AzureIMDS` follows Azure metadata-service retry guidance with capped additive backoff.

State, dependencies, and integration: calculator instances hold only tuning fields and, for Google Drive, a limiter. They depend on `math/rand`, `time`, `golang.org/x/time/rate`, and package-level helpers/types from `pacer` such as `State` and `IsRetryAfter`. Integration is indirect through the main Pacer implementation, which invokes `Calculate` between calls.

Risks and test signals: the random backoff uses package `math/rand`, which is fine for scheduling jitter but not security. Option updates rebuild the Google Drive limiter, so changing `MinSleep`/`Burst` resets rate state. Shifting durations by user-controlled constants can overflow if absurd values are supplied, though normal configuration bounds likely prevent this. This file is not directly tested in the requested set; it is covered by broader pacer tests outside the group.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacers.go -->
