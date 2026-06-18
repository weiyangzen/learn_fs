# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.cc

## Purpose

This file implements the concrete SSI client-side task object that sends one request over an `XrdSsiSessReal` endpoint, waits for the server response, exposes either a single data response or a streaming response to the original `XrdSsiRequest`, and handles asynchronous completion/cancellation. It is the active state-machine body for `XrdSsiTaskReal` from the companion header.

## Important APIs, types, and functions

The main public methods implemented here are `SendRequest`, `XeqEvent`, `XeqEvFin`, `SetBuff` for synchronous and asynchronous stream reads, `Kill`, `Detach`, `Finished`, `SchedError`, and `SendError`. Private helpers are `Ask4Resp`, `GetResp`, and `RespErr`. Local helper classes include `AlertMsg`, which wraps server alert payloads for `XrdSsiRRAgent::Alert`, and `SchedEmsg`, a scheduler job that calls `SendError`.

The task state names map the header enum values `isPend`, `isWrite`, `isSync`, `isReady`, `isDone`, and `isDead`. The file also owns constants used to disable XRootD read recovery before response waits, a zero-byte stand-in `zedData`, and a `voidSession` used for forced detachment.

## Control flow

`SendRequest` requires `isPend`, binds the target node into the request, calls `GetRequest`, builds an `XrdSsiRRInfo` write descriptor, fakes an empty request as one zero byte, and starts an asynchronous `epFile.Write`. A successful write marks `mhPend`; a failed write stores SSI error info and schedules an asynchronous error job.

`XeqEvent` is the central callback. In `isWrite`, it handles write failure, posts any killer semaphore, releases the request buffer, and calls `Ask4Resp`. `Ask4Resp` sends an SSI wait command via `epFile.Fcntl`, marks the task `isSync`, and unlocks the session while the wait is pending. In `isSync`, a successful response is parsed by `GetResp`: alert payloads are delivered and the wait is reissued, full responses call `SetResponse`, stream responses call `SetResponse((XrdSsiStream *)this)`, and malformed or missing responses become error responses. In `isReady`, the callback completes an async stream read and calls `ProcessResponseData` outside the session lock.

## State and persistence behavior

There is no durable persistence. Runtime state lives in the session, endpoint file, request pointer, deferred-callback counter, message-handler pending flag, response buffer ownership (`mdResp`), stream read buffer pointers, and the task state. The session mutex protects task state and lifetime. `defer` prevents `Finished` cleanup while callbacks might re-enter user code. `mhPend` tracks outstanding XrdCl callback ownership. `mdResp` holds an `AnyObject` response alive when metadata/data buffers inside it are handed to upper layers.

## Dependencies and integration points

The file integrates with `XrdSsiRRAgent` for request/responder binding, alerts, request buffers, and shared error info; with `XrdSsiSessReal` for locking and endpoint access; with `XrdCl::File` asynchronous `Write`, `Fcntl`, and `Read`; with `XrdScheduler` for deferred error delivery; and with `XrdSsiUtils` for XRootD-to-SSI error conversion and byte dumping.

## Risks and edge cases

Lifetime is the main risk. `Kill` can block waiting for an in-flight write callback via `XrdSysSemaphore` to avoid freeing request memory before XrdCl finishes using it. `RespErr` deliberately unlocks the session while posting an error response, so callers must reset lock guards correctly. The stream path allows only one async read at a time and treats short reads as EOF. `GetResp` trusts the wire-format header lengths after basic bounds checks; malformed prefix or metadata lengths produce generic invalid-response errors. Several comments note unusual or "ugly" cleanup sequencing, which is accurate: new callbacks must preserve `defer` and `mhPend` invariants.

## Test signals

Useful tests are asynchronous request success, write failure, response wait failure, alert followed by final response, full data response, stream response with sync and async reads, cancellation during write and during response wait, forced detach/orphan cleanup, invalid response headers, missing response objects, and short stream reads. Thread-sanitizer or stress tests are especially relevant because the file's correctness depends on session lock discipline and callback lifetime.
