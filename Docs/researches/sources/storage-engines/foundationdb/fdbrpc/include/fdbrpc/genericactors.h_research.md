## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/genericactors.h

Purpose: Provides coroutine/actor utility functions used by fdbrpc request/reply flows, especially retrying well-known endpoints, hostname resolution, promise forwarding, broadcasts, stream termination, and failure-raced waits.

Important APIs/types/functions: `retryBrokenPromise()` retries `getReply()` after broken promises. `tryGetReplyFromHostname()` and `retryGetReplyFromHostname()` resolve hostnames to well-known endpoints and clear DNS cache on connection failures. `timeoutWarning()` emits periodic warning signals while waiting. `forwardPromise()` overloads bridge futures to promises/reply promises/promise streams. `broadcast()` and incremental broadcast helpers fan out one result. `PeerHolder` tracks outstanding peer replies. `endStreamOnDisconnect()`, `waitValueOrSignal()`, `sendCanceler()`, and `reportEndpointFailure()` implement lower-level failure handling for fdbrpc primitives.

Control flow: Retry helpers loop, reset reply promises, delay/jitter/back off, and re-resolve hostnames as needed. `waitValueOrSignal()` races a value future with a failure signal and peer disconnect, converting failures into `ErrorOr` results and notifying the failure monitor on broken promises. `sendCanceler()` waits for a reliable reply while cancelling the reliable packet on completion or permanent failure.

State and persistence behavior: No durable state. Runtime state includes retry intervals, held peers, promise references, and DNS cache invalidation through the external `removeCachedDNS()`.

Dependencies and integration points: Includes Flow generic actors/coroutine utilities, `fdbrpc.h`, `WellKnownEndpoints`, `FailureMonitor`, and hostname resolution. It is included at the bottom of `fdbrpc.h`, so these helpers participate in core RPC behavior.

Risks: Retry loops can spin without the jitter/backoff knobs. Hostname cache invalidation must occur only on connection-like failures. `PeerHolder` outstanding reply counts must stay balanced. Error conversion in `waitValueOrSignal()` determines at-most-once retry safety.

Test signals: Broken-promise retry, hostname lookup failure, re-resolution after request_maybe_delivered, timeout warning cadence, promise forwarding success/error, incremental broadcast yielding, stream disconnect termination, peer disconnect handling, and reliable packet cancellation.
