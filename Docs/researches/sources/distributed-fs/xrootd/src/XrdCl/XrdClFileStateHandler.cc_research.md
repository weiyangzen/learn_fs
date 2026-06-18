# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileStateHandler.cc

## Purpose

`XrdClFileStateHandler.cc` implements the stateful backend for `XrdCl::File`. It owns the lifecycle of an open file handle, translates high-level file operations into XRootD protocol messages, tracks the current data server/session/file handle, dispatches requests through the client transport, and recovers outstanding operations after recoverable transport/session failures. The public `XrdCl::File` facade in `XrdClFile.cc` forwards nearly all non-plugin file operations here, including open/close, stat, read/write variants, page read/write, vector I/O, xattrs, checkpoint writes, clone, and explicit data-server failover.

The file also contains several anonymous-namespace response handlers that adapt low-level async responses back into the state machine:

- `PgReadHandler` validates returned page checksums and coordinates per-page retry reads.
- `PgReadRetryHandler` validates one retry page, updates the parent page checksum, and reports success/failure to `PgReadHandler`.
- `PgReadSubstitutionHandler` converts an ordinary read response into a `PageInfo` response when the server lacks page-read support.
- `OpenHandler` updates `FileStateHandler` on open completion and optionally hands EC redirects to an erasure-coding plugin when built with `WITH_XRDEC`.
- `CloseHandler` updates state on close completion and owns the close `Message`.
- `StatefulHandler` is the common wrapper for stateful operations; it routes failures to recovery/redirection handling and successful responses to accounting/caching before invoking the user handler.
- `ReleaseBufferHandler` preserves ownership of rvalue `Buffer` data while an async write is in flight.

## Important APIs, types, and functions

The constructors initialize the state as closed, allocate the 4-byte file-handle buffer, reset monitoring counters, register with the global fork handler and file timer, and allocate a `LocalFileHandler`. The destructor decrements file instance counts for physical remote connections, unregisters from timer/fork infrastructure, emits a close monitor event if destruction happens while open, releases virtual Metalink redirectors, and deletes owned state such as URLs, stat info, file handle, and local-file handler.

Open paths are split between `Open`, `OpenUsingTemplate`, and `OpenImpl`. `OpenUsingTemplate` requires a `FileStateHandlerTemplate` exported from another file and stores its weak pointer for `Dup`/`Samefs` open flags. `OpenImpl` validates current state, parses the URL, injects a unique `xrdcl.requuid` CGI value for replay safety, applies `xrdcl.recover-reads=false` and `xrdcl.recover-writes=false`, builds a `kXR_open` request with async/stat options, applies `FillFhTempl` when needed, and dispatches through `IssueRequest`.

Close is implemented by `Close`. It rejects close while another close, open, or recovery is active, and by default rejects close while requests remain in `pInTheFly` unless `BundledClose` is enabled. It builds a stateful `kXR_close` request for `pDataServer`. If send fails because the session/connection is already gone, it treats the file as closed and queues a synthetic successful close response through the `JobManager`.

Ordinary file operations are implemented as protocol request builders followed by `SendOrQueue`: `Stat`, `PreRead`, `Read`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `ReadV`, `Fcntl`, `Visa`, `SetXAttr`, `GetXAttr`, `DelXAttr`, `ListXAttr`, `Checkpoint`, `ChkptWrt`, `ChkptWrtV`, `Clone`, and the page I/O helpers. They share the same state guard: `Error` returns the stored status, and only `Opened` or `Recovering` may issue normal stateful operations.

Page I/O has extra logic. `PgRead` queries transport server flags and protocol version; if page read/write is unsupported, it falls back to `Read` and wraps the result as `PageInfo`. If supported, it sends `kXR_pgread` through `PgReadImpl`; `PgReadHandler` CRC32C-checks returned pages and retries corrupt pages via `PgReadRetry` with `kXR_pgRetry`. `PgWrite` computes or validates CRC32C digests, sends `kXR_pgwrite`, and retries corrupt pages reported by `RetryInfo` with `PgWriteRetry`, bounded by the remaining timeout.

Recovery and redirect helpers are the core state-machine internals. `OnStateError` handles stateful errors, maps redirect statuses into `OnStateRedirection` when redirects are enabled, reports monitor error events, fails nonrecoverable messages, and queues recoverable requests. `SendOrQueue` either queues during `Recovering` or sends during `Opened`, recording successfully sent messages in `pInTheFly`. `RecoverMessage` enters `Recovering`, tries to run recovery, and queues the request if recovery starts. `RunRecovery` waits for all in-flight messages to drain, then reopens at a state redirect, load balancer, or current data server. `ReOpenFileAtServer` rebuilds a `kXR_open` request, strips destructive `Delete`/`New` flags for recovery, and uses `OpenHandler` to finish state restoration. `ReSendQueuedMessages` updates session ids and file handles after a reopen and resends queued requests.

`OnOpen`, `OnClose`, and `OnStateResponse` maintain persistent in-memory state. `OnOpen` records `pDataServer`, `pLoadBalancer`, write-recovery redirector, encryption status, file handle, session id, stat info, and monitoring open event; it also clears `Dup`/`Samefs` after a successful template-based open. `OnClose` emits close monitoring and resets counters. `OnStateResponse` removes messages from `pInTheFly`, triggers recovery if the last in-flight request completed, updates cached stat info, and increments read/write/vector byte and operation counters.

`IssueRequest` selects the transport path: Metalink virtual redirector via `MessageUtils::RedirectMessage`, local file execution via `LocalFileHandler::ExecRequest`, or ordinary remote transport via `MessageUtils::SendMessage`. `FillFhTempl` validates and injects source file-handle/session information for `Dup`/`Samefs` open. `Clone` validates destination/source files are open on the same session and sends `kXR_clone` range descriptors. `WriteKernelBuffer` sends page-aligned buffers using `XrdSys::KernelBuffer`; recovery explicitly does not support kernel-buffer writes.

## Control flow

The normal open-to-I/O flow is:

1. `XrdCl::File` constructs a `FileStateHandler` and calls `Open` or `OpenUsingTemplate`.
2. `OpenImpl` moves the state from `Closed` to `OpenInProgress`, builds the open message, and dispatches through `IssueRequest`.
3. `OpenHandler` receives the response and calls `OnOpen`.
4. `OnOpen` either records failure, fails queued messages, and enters `Error`, or records file handle/session/server/stat state, resends any queued recovery messages, and enters `Opened`.
5. Each I/O method builds a protocol-specific message, wraps it in `StatefulHandler`, and calls `SendOrQueue`.
6. `StatefulHandler` sends success to `OnStateResponse` and then to the user handler; errors are routed to `OnStateError`.
7. `Close` sends `kXR_close`; `CloseHandler` calls `OnClose`, which emits monitoring and returns to `Closed`.

The recovery flow is:

1. A stateful request fails with a recoverable status, such as socket error, timeout, invalid session, internal error, TLS error, or interrupted operation.
2. `OnStateError` erases the message from `pInTheFly`, records monitoring, and calls `RecoverMessage` unless the message is nonrecoverable or uses a kernel buffer.
3. `RecoverMessage` marks `Recovering`, calls `RunRecovery`, and places the failed request in `pToBeRecovered` if recovery can proceed.
4. `RunRecovery` waits until no in-flight messages remain, optionally sends a best-effort close for redirect recovery, and reopens the file at a redirect, load balancer, or current data server.
5. The reopen response goes through `OnOpen`, which updates the new session and file handle and calls `ReSendQueuedMessages`.
6. `ReWriteFileHandle` patches queued request bodies so retried requests use the new handle.

The timer/fork flow is external but important. `FileTimer::Run` calls `Tick(now)` on registered handlers; `Tick` opportunistically locks and invokes `TimeOutRequests`, which fails queued recovery requests whose `MessageSendParams::expires` has passed. `ForkHandler::Child` calls `AfterForkChild`, which puts open recoverable files into `Recovering` and clears in-flight/queued request sets in the child, or marks the file `Error` when the current open mode lacks enabled recovery.

## State and persistence behavior

All state is process-local and protected by `pMutex`; there is no durable persistence. The important fields are `pFileState`, `pStatus`, `pStatInfo`, `pFileUrl`, `pDataServer`, `pLoadBalancer`, `pStateRedirect`, `pWrtRecoveryRedir`, `pFileHandle`, `pOpenMode`, `pOpenFlags`, `pToBeRecovered`, `pInTheFly`, `pSessionId`, recovery toggles, redirect behavior, channel-encryption state, bundled-close toggle, monitoring counters, `pLFileHandler`, plugin reference, and a weak template-file pointer.

`pStatInfo` is cached on successful open and refreshed on successful `kXR_stat`; `Stat(force=false)` returns a copy of this cached value without a network request. Monitoring counters are accumulated only in memory and emitted on close or destructor cleanup. `pOpenFlags` is mutated after successful template open and during recovery: `Dup`/`Samefs` are cleared after successful open, and `Delete`/`New` are removed before recovery open attempts to avoid destructive or non-idempotent replays.

`pToBeRecovered` stores `Message*`, `ResponseHandler*`, and `MessageSendParams`; ownership transfers are delicate because `StatefulHandler` owns message and send-param payloads in normal completion, while queued recovery holds those same objects until resend or failure. `pInTheFly` is a set of raw `Message*` used to block recovery until outstanding requests settle and to enforce non-bundled close.

## Dependencies and integration points

This implementation depends heavily on XRootD client infrastructure: `MessageUtils` for request allocation/body encoding/send-param processing, `XRootDTransport` for message descriptions, `PostMaster` and `JobManager` for transport queries and async response jobs, `DefaultEnv` for global log/env/monitor/timer/fork/postmaster access, `XrdClStatus`, `XrdClURL`, `XrdClXRootDResponses`, and protocol structs from `XProtocol`. `LocalFileHandler` handles `file://` URLs, and `RedirectorRegistry` tracks virtual Metalink redirectors.

External integrations include `XrdCl::File`, which is the public caller; `XrdClFileTimer`, which drives recovery timeout checks; `XrdClForkHandler`, which locks and repairs handlers across fork; `XrdClClassicCopyJob`, POSIX bridge code, S3/HTTP/client plugins, and record/replay plugins, which exercise page I/O, recovery properties, `TryOtherServer`, and delegated public `File` methods. Optional `WITH_XRDEC` support allows an EC handler to replace the file plugin after an EC redirect, with template-file opens rejected for that plugin path.

## Risks and edge cases

Memory ownership is high risk. Many methods allocate `Message`, `ChunkList`, `StatefulHandler`, and response objects manually. Early returns after partial message construction can leak if not paired with the expected handler ownership path; for example `XAttrOperationImpl` returns immediately on `CreateXAttrBody` failure after allocating a message. `Clone` can return validation errors after allocating a message if a later clone source is invalid. These patterns require audit when changing validation order.

Recovery correctness depends on request idempotency and handle rewriting. Read-only recovery can reopen through a load balancer, while write recovery usually reopens the same server or explicit write-recovery redirect. Non-idempotent opens are partially mitigated by stripping `Delete` and `New`, and by adding `xrdcl.requuid`, but write replay semantics still depend on server support and user-selected `WriteRecovery`.

Concurrency is subtle. The code mixes `XrdSysMutex`, callback-driven deletion of `this` in helper handlers, raw pointers in `pInTheFly`, and response callbacks that may trigger recovery before the user handler runs. Deadlocks are avoided by releasing some locks before deleting handlers in page-read paths, but new code must be careful not to call user handlers while holding the file mutex unless that is already established.

Page I/O has data-integrity risk surfaces. `PgReadHandler` validates CRCs and retries corrupt pages, but fallback `PgReadSubstitutionHandler` only computes checksums for encrypted channels; otherwise it can return an empty checksum vector for ordinary `Read` substitution. `PgWrite` retry status is mediated by a shared context whose destructor calls the user handler; multiple retry callbacks can race to set the final status if transport threading changes.

Close semantics are intentionally restrictive. Unless `BundledClose` is enabled, `Close` fails while messages are in flight. Enabling bundled close permits close with outstanding operations, so callers must tolerate completion ordering and monitor accounting effects.

Template and clone operations rely on weak references and same-session checks. The source template must remain alive and open; `FillFhTempl` changes the destination send URL to the template data server and requires `kXR_samefs` support. `Clone` requires all sources share the destination `pSessionId`, so recovery or redirect that changes session placement can invalidate later clone attempts.

## Test signals

There is no obvious focused unit-test file for `FileStateHandler` in the visible source tree. Useful test coverage should therefore be integration-heavy:

- Public `XrdCl::File` open/read/write/stat/close tests against a local XRootD server, verifying state transitions, cached stat behavior, and monitor counters.
- Failure-injection tests for socket timeout, invalid session, redirect during stateful request, and fork child behavior, asserting queued messages are resent with rewritten handles.
- Page-read/page-write tests with server support enabled and disabled, covering CRC mismatch retry, retry failure, substitution through ordinary `Read`, and timeout accounting across page-write retries.
- Template open and clone tests covering missing/invalid template, closed template, unsupported samefs, session mismatch, and successful `Dup`/`Samefs`/`kXR_clone` flows.
- Local-file and Metalink tests to ensure `IssueRequest` chooses `LocalFileHandler`, virtual redirector, or remote send correctly.
- Close tests for in-flight requests with and without `BundledClose`, and invalid-session close treated as already closed.
