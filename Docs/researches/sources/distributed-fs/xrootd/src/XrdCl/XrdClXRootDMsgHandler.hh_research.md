# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.hh

## Purpose
`XrdClXRootDMsgHandler.hh` declares `XRootDMsgHandler`, the `MsgHandler` implementation responsible for one XRootD client request, plus `RedirectEntry` for retry/redirect tracebacks. It defines the handler's public transport interface, private recovery/parsing helpers, and all state needed for asynchronous protocol processing.

## Important APIs, Types, And Functions
- `RedirectEntry` records `from`, `to`, redirect/retry/wait type, final status, and formats diagnostic trace entries.
- `XRootDMsgHandler` constructor wires request, user response handler, current URL, SID manager, local-file handler, default flags, and an async body reader selected by request id (`readv`, `read`, or discard).
- Public overrides implement `Examine`, `InspectStatusRsp`, `GetSid`, `Process`, `ReadMessageBody`, `OnStreamEvent`, `OnStatusReady`, `IsRaw`, and `WriteMessageBody`.
- Configuration setters include expiration, redirect-as-answer, oksofar-as-answer, load balancer, host list, chunk list, CRC digests, kernel buffer, redirect counter, metalink following, and stateful mode.
- Private helpers cover error recovery, retry, response parsing, request rewriting, tried-CGI updates, refresh flags, local redirects, retry eligibility, metalink wait omission, retriable error classification, traceback dumping, and buffer reads.
- `ChunkStatus`, constants `CksumSize`, `PageWithCksum`, `MaxSslErrRetry`, and `NbPgPerRsp` support page read/write checksum handling.

## Control Flow
The header shows the split between transport-facing callbacks and private state-machine methods. The handler starts with a marshaled request and becomes the rendezvous point for send notifications, incoming response headers/bodies, raw socket I/O, timer wakeups, and user callbacks. Atomic flags in `pSendingState` encode send done, response seen, final response, ready-to-send, retry-at-server, and in-flight completion milestones.

## State And Persistence Behavior
`XRootDMsgHandler` stores transient per-request state only. It may own `pRequest`, shares response messages with the message reader, owns partial responses, condition variables for oksofar-as-answer synchronization, raw-reader instances, redirect traceback entries, host list, redirect/effective data-server URLs, and mutable retry counters. Fields such as `pAsyncOffset`, `pAsyncChunkIndex`, and PgWrite checksum fields persist across socket retry writes within the same request.

## Dependencies And Integration Points
The header ties together `PostMasterInterfaces`, response models, `DefaultEnv`, `Message`, XRootD protocol headers, async readers, pthread/condvar utilities, kernel buffers, page-size helpers, `XrdOucPgrwUtils`, sockets, URLs, local-file handling, and SID management. Any module creating XRootD requests through the transport depends on this contract.

## Risks And Edge Cases
- The class is self-deleting after final responses, so public callbacks must not access it afterward.
- `pRequest` ownership changes when session IDs are present; destructor behavior depends on `pHasSessionId`.
- `pChunkList`, `pKBuff`, `pResponseHandler`, and `pLFileHandler` are raw pointers with lifetimes managed externally or by convention.
- `NbPgPerRsp` is sensitive to page alignment and checksum bytes; protocol changes require careful updates.
- Condition-variable use for oksofar responses must avoid deadlocks while partial responses are processed.

## Test Signals
Compile and behavioral coverage should exercise constructor reader selection, setter side effects (`SetChunkList` resizing status vector), `NbPgPerRsp` alignment cases, self-deletion final callback ownership, oksofar synchronization, and raw pointer lifetime assumptions under redirects and local-file handling.
