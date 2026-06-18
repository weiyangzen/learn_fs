# sources/storage-engines/tikv/components/tikv_util/src/stream.rs

## Purpose
Provides stream and retry utilities for external IO paths: converting `AsyncRead` into a byte stream, blocking on Tokio-based external IO, exponential-backoff retry helpers, and timeout wrapping.

## Important APIs, Types, and Functions
- `AsyncReadAsSyncStreamOfBytes<R>` wraps an `AsyncRead` in a `Mutex` and reusable 2 MiB buffer, implementing `Stream<Item=io::Result<Bytes>>`.
- `error_stream` returns a one-item error stream.
- `block_on_external_io` creates a current-thread Tokio runtime and blocks on a future.
- `RetryError`, `RetryExt`, `JustRetry`, `retry`, `retry_all_ext`, `retry_ext`, and `retry_expr!` implement retry policy.
- `with_timeout` maps Tokio timeout expiry into a boxed error conversion.

## Control Flow
The read stream polls the inner reader into the reusable buffer and copies the read slice into `Bytes`; zero bytes ends the stream. Retry starts at a one-second delay, invokes optional failure hooks, checks retryability, caps attempts, sleeps with random 0-999 ms jitter, and doubles delay up to `max_retry_delay`. `retry_ext` also honors a `retry_count` failpoint override.

## State and Persistence Behavior
Stream state is the reader plus buffer. Retry state is local per call: attempt count, delay, extension hook, and max values. No persistent state exists.

## Dependencies and Integration Points
Depends on `bytes`, `futures`, `futures_util::io::AsyncRead`, `tokio`, `rand`, and `fail`. Intended for object storage/external file IO paths that need manual retry behavior.

## Risks
`block_on_external_io` must not be nested, as documented. The stream copies bytes out of the reusable buffer each poll. Retry macros evaluate the action expression multiple times and can hide capture subtleties; callers should prefer function forms where possible. `with_timeout` requires an `Unpin` future.

## Test Signals
Tests verify retry futures remain `Send` with a non-`Sync` output type and use a failpoint to confirm retry-count failure/success boundaries.
