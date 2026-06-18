# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.cc

## Purpose
`XrdClXRootDMsgHandler.cc` implements the main per-request XRootD protocol response handler. It matches incoming server responses to a request, decides whether bodies should be read normally or in raw mode, unmarshals protocol responses, handles redirects/waits/errors/retries, writes raw request bodies, parses typed responses for user handlers, manages stream IDs, and coordinates final callback delivery.

## Important APIs, Types, And Functions
- Local `WaitTask` resends a request after a `kXR_wait` delay; `HandleRspJob` moves callback processing to the job manager when needed.
- `Examine` matches stream IDs, classifies response statuses, sets up raw readers, handles partial `kXR_oksofar` and `kXR_status`, and returns transport action flags such as `Raw`, `RemoveHandler`, `NoProcess`, and `Ignore`.
- `InspectStatusRsp` unmarshals V2 status bodies for page read/write and decides whether more raw data or retry data must be read.
- `Process` unmarshals normal bodies, updates host protocol/flags, handles `kXR_ok`, `kXR_status`, `kXR_oksofar`, `kXR_error`, `kXR_redirect`, `kXR_wait`, `kXR_waitresp`, and invalid responses.
- `ReadMessageBody` delegates raw reads to `AsyncPageReader` for `pgread` or `pBodyReader` for read/readv/discard cases.
- `OnStatusReady` reconciles send-completion notifications with possibly already received responses and delayed retries.
- `IsRaw` and `WriteMessageBody` handle raw request bodies for write, writev, pgwrite, and checkpoint-execute requests, including kernel-buffer and TLS fallback behavior.
- `HandleResponse`, `ProcessStatus`, `ParseResponse`, and `ParseXAttrResponse` build `XRootDStatus`/`AnyObject` results and invoke the user's `ResponseHandler`.
- `RewriteRequestRedirect`, `RewriteRequestWait`, `UpdateTriedCGI`, and `SwitchOnRefreshFlag` mutate marshaled requests across redirect/wait/retry paths.
- `HandleError`, `RetryAtServer`, `HandleLocalRedirect`, `IsRetriable`, `OmitWait`, `RetriableErrorResponse`, and `DumpRedirectTraceBack` implement recovery policy and diagnostics.

## Control Flow
Outgoing send status and incoming response status race through `pSendingState` flags. On incoming data, `Examine` takes ownership of matching responses and tells the transport whether raw body handling is needed. `Process` then unmarshals and either completes, parses partial data, schedules waits, follows redirects, or calls `HandleError`. Recoverable errors can update `tried` CGI, refresh flags, and requeue the same request through `RetryAtServer`; fatal or expired conditions flow to `HandleRspOrQueue` and then `HandleResponse`. Final responses release stream IDs when appropriate, transfer host-list ownership to `HandleResponseWithHosts`, and delete the handler.

## State And Persistence Behavior
The handler owns the request unless it carries a session ID, current and partial responses, a response handler pointer, current URL, host trace, optional load balancer, SID manager, redirect counters, not-authorized retry counter, raw reader/writer offsets, PgWrite checksum cursor state, partial directory-list state, timeout fence, and redirect traceback. It mutates the in-memory request buffer during redirects/waits/retries and maintains `pHosts` as a path history. It does not persist durable state, but its request mutations affect subsequent sends on the same handler.

## Dependencies And Integration Points
This file is a central integration point for `PostMaster`, `TaskManager`, `JobManager`, `SIDManager`, `Message`, `MessageUtils`, `XRootDTransport`, `LocalFileHandler`, `RedirectorRegistry`, async raw/vector/page readers, sockets, TLS state, Xrd protocol structs/constants, `XrdOucPgrwUtils`, CRC/page-size helpers, and `DefaultEnv` configuration. It feeds typed objects defined in `XrdClXRootDResponses.hh` to user-facing response handlers.

## Risks And Edge Cases
- Send-completion and response-arrival races are subtle; incorrect `pSendingState` transitions can leak SIDs, invoke callbacks too early, or use a deleted handler.
- Redirect handling preserves selected CGI keys and credentials, rewrites paths, may collapse redirects, and can turn non-XRootD redirects into user-visible answers; small URL parsing changes can affect auth and recovery.
- Raw `pgwrite` writes checksum/data page pairs and tracks several offsets; off-by-one errors corrupt payload framing.
- `ParseResponse` contains many request-specific parsers; malformed lengths can cause invalid-response errors, but any missing guard risks buffer misuse.
- Retriable errors are policy-heavy and environment-dependent (`OpenRecovery`, `NotAuthorizedRetryLimit`, `MaxMetalinkWait`).
- `HandleLocalRedirect` bypasses normal final handling and deletes `this` after invoking local file handling.
- Manual ownership of `AnyObject`, response objects, host lists, requests, and self-deleting handler lifecycle increases leak/double-delete risk.

## Test Signals
High-value tests include response/request stream-ID matching, ok/oksofar/status partial read flows, read/readv raw body handling, pgread checksum/page framing and size mismatch detection, pgwrite retry body parsing, redirect URL/CGI preservation, redirect limits, wait scheduling and expiration, retriable errors through meta-manager and virtual redirector load balancers, TLS transient error downgrade limit, SID release/timeout behavior, local-file redirects, xattr parsing for set/get/list, and send/response race ordering.
