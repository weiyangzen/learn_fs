## sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry.go

Purpose: Classifies storage errors for retry and records retry metrics.

Important APIs/types/functions: `retryAction` enum, `determineRetryAction`, `ShouldRetryWithoutLogging`, `ShouldRetry`, and `ShouldRetryWithMonitoring`.

Control flow: `determineRetryAction` first delegates to `storage.ShouldRetry`, then special-cases HTTP 401 `googleapi.Error` and gRPC `codes.Unauthenticated` for credential-refresh retries. Logging variants emit warning messages; monitoring variant records `metrics.GcsRetryCount` for retryable errors and distinguishes `context.DeadlineExceeded` as stalled read requests.

State and persistence behavior: no persistent state; writes logs and metrics through global logger/metric handle.

Dependencies and integration points: used by generic retry executor and storage operations. Coupled to Cloud Storage SDK retry policy, Google API errors, gRPC status codes, and generated metric attributes.

Risks: retrying 401/Unauthenticated is a workaround for token timing issues and can hide persistent auth failures until retry budgets expire. `ShouldRetryWithMonitoring` assumes non-nil metric handle. Logging can be noisy on repeated transient errors.

Test signals: `custom_retry_test.go` covers 401/429/502, 400, unexpected EOF, network reset/refused, gRPC Unauthenticated, non-logging behavior, log contents, and metric category recording.
