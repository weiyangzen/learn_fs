# sources/object-store/rustfs/crates/utils/src/retry.rs

## Purpose
Provides retry timing and retryability classification for S3/HTTP/request errors.

## Important APIs, Types, And Functions
Constants include `MAX_RETRY`, jitter bounds, and default retry unit/cap durations. `RetryTimer` is a `Stream<Item = ()>` with configurable max retries, base sleep, cap, jitter, and random factor. Retry classifiers are `is_s3code_retryable`, `is_s3code_in_message_retryable`, `is_http_status_retryable`, and `is_request_error_retryable`. Static retryable S3 codes include throttling, timeout, internal error, expired token, and slowdown variants; HTTP statuses include 408, 429, 500, 502, 503, and 504.

## Control Flow And State
`RetryTimer::poll_next` computes exponential backoff from remaining attempts, caps it, optionally subtracts jitter, initializes or resets a Tokio interval, and yields until attempts are exhausted. Classifiers use immutable `LazyLock<Vec<_>>` lists. Request error classification matches selected transient `ErrorKind` values.

## Dependencies And Integration Points
Uses `futures::Stream`, `hyper::http::StatusCode`, and `tokio::time::Interval`. Compiled only when `net` and `io` features are enabled.

## Risks And Test Signals
The timer uses `base_sleep * (1 << attempt)`, so very large retry counts can overflow shift/multiplication before the cap is applied. Substring S3 matching is intentionally case-sensitive and can produce false positives if retryable code text appears in unrelated messages. Tests cover stream retry count/zero retries and S3 message matching behavior.
