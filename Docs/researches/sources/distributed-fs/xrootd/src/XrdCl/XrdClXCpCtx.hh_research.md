# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.hh

## Purpose
`XrdClXCpCtx.hh` declares `XCpCtx`, the shared coordination object for the extreme-copy implementation. It documents the producer/consumer model where `XCpSrc` threads fetch chunks from multiple replicas and a caller consumes completed `PageInfo` objects from a synchronized sink.

## Important APIs, Types, And Functions
- Constructor accepts replica URLs, block size, parallel source count, chunk size, per-source chunk parallelism, and optional known file size.
- `Delete`, `Release`, and `Self` are the reference-counting API.
- `GetNextUrl`, `WeakestLink`, `RemoveSrc`, and `NotifyIdleSrc` are source coordination APIs.
- `PutChunk`, `GetChunk`, `GetBlock`, `SetFileSize`, and `GetSize` form the transfer coordination API.
- `Initialize` starts source threads.
- `AllDone` blocks idle sources until global completion, source failure, or timeout.
- Private state includes `pUrls`, `pSources`, `pSink`, `pOffset`, `pFileSize`, `pDataReceived`, completion/delete condition variables, and mutex/refcount fields.

## Control Flow
The intended lifecycle is: construct context, call `Initialize`, let sources call `Self()` and `Release()`, consume chunks through `GetChunk`, and finally call `Delete()` exactly once. `GetSize` waits on `pFileSizeCV` until `SetFileSize` publishes a non-negative file size or no sources remain running. The header explicitly records lock-order requirements for `pFileSizeCV`/`pMtx` and `pMtx`/`pDeleteCV`.

## State And Persistence Behavior
The class owns in-memory coordination state only. It does not own `pSources` pointers according to the comments; sources remove themselves on destruction. It owns queued `PageInfo*` chunks in `pSink` until the consumer takes them or the destructor frees leftovers. The reference-counting fields ensure the context outlives source threads.

## Dependencies And Integration Points
The header depends on `XrdClSyncQueue.hh`, `XrdClXRootDResponses.hh` for `PageInfo`, and `XrdSysPthread.hh`. It forward-declares `XCpSrc`, avoiding a full source-header dependency in the declaration. Higher-level copy code includes this header to start and consume multi-source transfers.

## Risks And Edge Cases
- `Delete()` must only be called once; the header states this but does not enforce it.
- The source list contains non-owned raw pointers, so source destruction/removal races are controlled only by the class's mutex and manual references.
- The `pDone` flag doubles as successful completion and failure shutdown signal for idle sources.
- `uint8_t` parallelism fields can overflow or truncate if callers pass larger values before construction.

## Test Signals
Useful tests exercise lifecycle ordering, concurrent `Self`/`Release`, blocking and wakeup of `GetSize`, all `GetChunk` status codes, and `WeakestLink` returning a retained source that remains valid until `Delete()`.
