## sources/object-store/minio-mc/pkg/limiter/limiter.go

Purpose: wraps an `http.RoundTripper` to apply upload and download throughput limits using token buckets. Important APIs are `New`, `RoundTrip`, and `limitReader`.

Control flow returns the original transport when both limits are zero; otherwise it creates upload/download buckets for positive limits. During `RoundTrip`, request bodies are replaced with a read-closer whose reader is rate-limited, the underlying transport is called, and response bodies are similarly wrapped. State is the bucket pair and underlying transport. Dependencies are `net/http`, `io`, and `juju/ratelimit`. Risks include nil transport errors, shared bucket behavior across concurrent requests, wrapping response bodies even when the underlying transport returns both response and error, and no tests in this subset.
