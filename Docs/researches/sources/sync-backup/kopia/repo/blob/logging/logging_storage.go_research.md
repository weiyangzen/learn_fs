# sources/sync-backup/kopia/repo/blob/logging/logging_storage.go

Purpose: wraps a `blob.Storage` to log operations, durations, errors, concurrency levels, and OpenTelemetry spans.

Important APIs/types/functions: `loggingStorage`, `beginConcurrency`, `endConcurrency`, operation wrappers for `GetBlob`, `GetCapacity`, `IsReadOnly`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `Close`, `ConnectionInfo`, `DisplayName`, `FlushCaches`, `ExtendBlobRetention`, `translateError`, and `NewWrapper`.

Control flow: most operations start an OTel span, increment concurrency, start a timer, delegate to the base storage, record structured debug logs and content-log entries, then return the original error. `beginConcurrency` tracks and logs new maximum concurrency using atomics. `ListBlobs` wraps the callback to count results. `translateError` shortens blob-not-found logging to a string while leaving other errors intact.

State and persistence behavior: wrapper state is in-memory counters and references to loggers/base storage. It does not alter blob persistence, except timing/log side effects. Content logs may be persisted depending on configured logger sinks.

Dependencies/integration points: integrates with OpenTelemetry, Kopia `contentlog`, `logging.Logger`, `blobparam`, `logparam`, and any underlying storage. Risks include logging sensitive blob IDs/metadata, content-log overhead, concurrency count imbalance if panics occur, and a duplicated `"ListBlobs"` argument in content logging. Tests cover basic delegation/logging behavior.
