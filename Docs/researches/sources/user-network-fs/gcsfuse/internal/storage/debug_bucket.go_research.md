# sources/user-network-fs/gcsfuse/internal/storage/debug_bucket.go

## Purpose
`debug_bucket.go` implements a logging decorator for `gcs.Bucket`. It traces bucket operations, request IDs, durations, errors, upload progress callbacks, reader close timing, and multi-range downloader activity while preserving the wrapped bucket behavior.

## Important APIs, Types, and Functions
`NewDebugBucket` returns a `debugBucket` around a wrapped bucket. `debugBucket` stores the wrapped `gcs.Bucket` and an atomic `nextRequestID`. Helper methods `mintRequestID`, `requestLogf`, `startRequest`, and `finishRequest` produce trace logs. `debugReader` wraps `gcs.StorageReader` to log read errors and final close status. `debugMultiRangeDownloader` wraps `gcs.MultiRangeDownloader` to trace `Add`, `Close`, `Wait`, and `GetHandle`.

The bucket implementation forwards `Name`, `BucketType`, `NewReaderWithReadHandle`, create/write/finalize/flush, copy/compose/stat/list/update/delete/move, folder operations, `NewMultiRangeDownloader`, and `GCSName`.

## Control Flow
Each operation starts by minting a request ID, formatting a human-readable description, and logging an incoming line. Most methods defer `finishRequest` so duration and final error are logged. Reader creation logs the request immediately; if creating the wrapped reader fails, it logs completion at once, otherwise it returns `debugReader`, which delays final completion logging until `Close`. Upload methods install a default progress callback when the caller did not provide one.

Multi-range downloader creation logs the constructor and wraps the returned downloader. Each `Add` call logs a separate range request and wraps the callback so completion is logged when the underlying range finishes. `Wait` and `Close` are also traced. `Error` delegates without logging; `GetHandle` logs as an operation.

## State and Persistence Behavior
The only internal state is the monotonically increasing request ID counter. The wrapper has no durable persistence and does not mutate bucket data except by delegating to the wrapped bucket. Side effects are trace logs and default progress callbacks added to request structs.

## Dependencies and Integration Points
The file depends on `logger.Tracef`, `gcs` interfaces and request types, `cloud.google.com/go/storage` read handles, `io`, `sync/atomic`, `time`, and `context`. It can be layered around any `gcs.Bucket`, including fake, cached, or real buckets, to diagnose storage behavior.

## Risks and Edge Cases
Because progress callbacks may be written into caller-provided request structs, callers reusing requests can observe the mutation. Request descriptions include object and folder names, so trace logs can contain user data. `setupReader` always calls `NewReaderWithReadHandle`; if future bucket interfaces distinguish reader methods, this wrapper must be updated. Multi-range `Add` logs completion only when callbacks run; if an implementation never invokes callbacks, those request logs remain unfinished.

## Test Signals
There are no direct tests in this subset. Compile-time conformance to `gcs.Bucket` and behavior observed through higher-level storage tests are the main signals. Useful tests would assert wrapped delegation, request ID uniqueness under concurrency, reader close logging, callback preservation, and nil-callback progress logging.
