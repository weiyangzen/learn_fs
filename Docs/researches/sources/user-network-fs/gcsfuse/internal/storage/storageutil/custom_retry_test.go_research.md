## sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry_test.go

Purpose: Unit tests for custom retry classification, logging, and retry metrics.

Important APIs/types/functions: tests cover `ShouldRetry`, `ShouldRetryWithoutLogging`, `determineRetryAction`, and `ShouldRetryWithMonitoring`; helper `logBuffer` captures logger output; `fakeMetricHandle` records retry metric calls.

Control flow: table-driven tests pass representative errors from Google API, gRPC status, net/url wrappers, context deadlines, and generic errors, then assert retry decision or metric/log side effects.

State and persistence behavior: temporarily redirects the global logger output and restores it to `os.Stdout`. No files or external services are used.

Dependencies and integration points: verifies assumptions about `storage.ShouldRetry` for network and HTTP classes, plus integration with generated `metrics.RetryErrorCategory` values.

Risks: retry classification inherited from `cloud.google.com/go/storage` may change. String-based network error cases depend on SDK behavior.

Test signals: strong coverage of retry edge cases, especially credential-refresh workarounds and stalled-read metric tagging.
