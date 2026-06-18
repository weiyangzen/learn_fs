# sources/user-network-fs/blobfuse2/component/azstorage/policies_test.go

Purpose: `policies_test.go` validates the custom Azure SDK rate-limiting policy used by BlobFuse2 azstorage clients.

Important APIs, types, and functions: The file defines `mockTransport`, `policiesTestSuite`, `SetupTest`, `TearDownTest`, and tests for `newRateLimitingPolicy`. Tests construct Azure SDK runtime pipelines with the policy in `PerRetry` and a mock transport returning HTTP 200. Assertions use Testify suite/assert helpers and the BlobFuse2 logger is set to silent debug mode for isolation.

Control flow: Each test creates a pipeline, builds an SDK request, and invokes `pipeline.Do`. The ops and bandwidth tests consume the 10-second burst capacity, then measure the next request and require at least roughly 900 ms of delay for a 1 op/sec or 100 bytes/sec limiter. The no-limit and non-GET tests execute loops expected to remain below 100 ms.

State and persistence behavior: The tests depend on rate limiter token-bucket state across repeated requests in a single pipeline. They do not touch Azure storage or persistent filesystem state. Logger state is initialized and destroyed per test to avoid cross-suite contamination.

Dependencies and integration points: The suite uses Azure SDK `runtime.NewPipeline`/`NewRequest`, BlobFuse2 `common` and `log`, Go `net/http`, `context`, and `time`. It indirectly depends on `parseRangeHeader` from `utils.go` because bandwidth limiting is range-size based.

Risks: Timing assertions can be flaky on overloaded CI hosts or systems with coarse scheduling. Tests reuse the same request object for repeated `pipeline.Do` calls, which matches the policy's needs but may not model all SDK request lifecycles. Coverage focuses on rate limiting only and does not validate telemetry or service-version policies in the same file.

Test signals: Positive signals include explicit coverage for ops limiting, byte limiting with `Range`, byte limiting with lower-case `x-ms-range`, disabled limiters, and non-GET bypass. Missing signals include malformed range error behavior, context cancellation while waiting, burst clamping, and mixed ops-plus-bandwidth limiting.
