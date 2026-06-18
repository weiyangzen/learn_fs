# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.hh

## Purpose
Declares the SSI alert callback object that bridges response alert messages into XRootD error-info callback delivery.

## Important APIs, Types, And Functions
- `XrdSsiAlert : XrdOucEICB` with public `next` for free-list linking.
- Static `Alloc()`, `SetMax()`, and instance `Recycle()`.
- `SetInfo()` populates `XrdOucErrInfo` with metadata for alert transmission.
- `Done()` and `Same()` implement `XrdOucEICB`; `Same()` always returns false.

## Control Flow
Users allocate alerts through `Alloc()` rather than constructing directly, pass them as callbacks, then `Done()` recycles them after the underlying query/response signal completes. Pool sizing is controlled with `SetMax()`.

## State And Persistence
The class owns static pool state and per-object pointer `theMsg` to the response message currently being delivered. It persists only reusable callback objects in memory.

## Dependencies And Integration Points
Includes `XrdOucErrInfo`, `XrdSsiRequest.hh`, and `XrdSysPthread.hh`. The callback inheritance connects it to OUC async response machinery.

## Risks And Edge Cases
Because `next` is public and used for pooling, external misuse could corrupt the free list. The header does not document ownership expectations for `theMsg` or callback error info; the implementation assumes `Done()` owns `eiP`.

## Test Signals
Compile tests for `XrdOucEICB` compatibility, allocation/recycle lifecycle tests, pool size changes via `SetMax()`, and callback dispatch tests through SSI request paths.
