# sources/user-network-fs/rclone/lib/pacer/pacer_test.go

Source read signal: reviewed complete local file (480 lines, sha256 2f7f96b6510486e2).

Purpose: Tests pacer defaults, calculator behavior, call/retry flow, max-connection limiting, recursive deadlock avoidance, and retry-after error wrapping.

Important APIs/types/functions: Covers `New`, setters, `beginCall`, `endCall`, `Call`, `CallNoRetry`, default/Azure/GoogleDrive/S3 calculators, `RetryAfterError`, `Cause`, and `IsRetryAfter`.

Control flow: Tests drain tokens to control timing, use dummy paced functions and condition variables to observe concurrency, run retries with fixed counts, average randomized Google Drive sleeps, and verify nested retry-after errors through wrapping.

State and persistence behavior: Uses in-memory pacer channels and goroutines; no persistence.

Dependencies and integration points: Uses `sync`, `time`, `errors`, `strings`, `fmt`, and `testify/assert`. It reaches calculator types from sibling files, so it tests package-level integration beyond `pacer.go`.

Risks and test signals: Strong timing/concurrency signal, but timing tests can be sensitive under slow CI. Recursive deadlock tests protect the stack-inspection workaround.
