# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileStateHandler.hh

## Purpose

`XrdClFileStateHandler.hh` declares the private stateful implementation behind `XrdCl::File`. It exposes a static-method API that takes a `std::shared_ptr<FileStateHandler>& self`, allowing async helper handlers to retain object lifetime while operations are in flight. The class is not the public file API; it is the internal state machine that owns file state, recovery queues, file-handle/session metadata, local-file dispatch, optional file plugin linkage, and monitoring counters.

The header also declares `PgReadFlags`, a small flag enum for page-read retry requests, and `FileStateHandlerTemplate`, the `ExportedFileTemplate` implementation used by `File::OpenUsingTemplate` and `File::Clone` to carry a weak pointer to an already-open handler.

## Important APIs, types, and functions

`FileStateHandler::FileStatus` defines the lifecycle states: `Closed`, `Opened`, `Error`, `Recovering`, `OpenInProgress`, and `CloseInProgress`. Most implementation methods enforce these states before building protocol messages.

The public static operation surface mirrors `XrdCl::File`: `Open`, `OpenUsingTemplate`, `Close`, `Stat`, `PreRead`, `Read`, `PgRead`, `Write` overloads, `PgWrite`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `ReadV`, `Fcntl`, `Visa`, xattr operations, `Checkpoint`, checkpointed writes, `Clone`, `TryOtherServer`, and `ExportTemplate`. Page I/O is split into public entry points and internal retry/implementation functions: `PgReadRetry`, `PgReadImpl`, `PgWriteRetry`, and `PgWriteImpl`.

Lifecycle callbacks declared in the header are `OnOpen`, `OnClose`, `OnStateError`, `OnStateRedirection`, and `OnStateResponse`. These are called by anonymous-namespace response handlers from the `.cc` file and are the main transition points after async transport responses.

Operational state accessors and controls include `IsOpen`, `IsSecure`, `SetProperty`, `GetProperty`, `Lock`, `UnLock`, `Tick`, `TimeOutRequests`, `AfterForkChild`, and `NeedFileTempl`. `Lock`/`UnLock` are used by fork handling, while `Tick` and `TimeOutRequests` are used by the file timer.

Private helper types include `RequestData`, a triple of `Message*`, `ResponseHandler*`, and `MessageSendParams`, and `RequestList`, a `std::list<RequestData>` used for recovery. Private helpers include `XAttrOperationImpl`, `SendOrQueue`, `IsRecoverable`, `RecoverMessage`, `RunRecovery`, `SendClose`, `IsReadOnly`, `ReOpenFileAtServer`, `FailMessage`, `FailQueuedMessages`, `FillFhTempl`, `OpenImpl`, `ReSendQueuedMessages`, `ReWriteFileHandle`, `ResetMonitoringVars`, `MonitorClose`, `IssueRequest`, and `WriteKernelBuffer`.

## Control flow

The declaration makes the intended layering clear. Public `File` methods call static `FileStateHandler` methods with the shared handler. Those methods acquire `pMutex`, validate `pFileState`, construct protocol messages, and call `SendOrQueue`. `SendOrQueue` either sends immediately when `Opened` or defers the request into recovery handling when `Recovering`.

Open is special because it establishes the state required by all other calls. `Open` clears any previous template weak pointer and calls `OpenImpl`; `OpenUsingTemplate` stores a template weak pointer and calls the same implementation. `NeedFileTempl` encodes the condition for template-required flags: `OpenFlags::Dup` or `OpenFlags::Samefs`.

Recovery is declared as a queue-driven flow. `OnStateError` decides whether a failed request can recover, `RecoverMessage` places it in recovery, `RunRecovery` performs reopen when no in-flight messages remain, `ReOpenFileAtServer` gets a new session and handle, and `ReSendQueuedMessages` uses `ReWriteFileHandle` before retrying saved messages. `Tick`/`TimeOutRequests` provide timeout cleanup for entries stuck in the recovery list.

Fork handling is integrated by exposing `Lock`, `UnLock`, and `AfterForkChild`. The fork handler can quiesce all file handlers before fork and then ask each child-side handler to enter a recoverable state or error state depending on open mode and recovery toggles.

## State and persistence behavior

The class persists all state only in memory. It owns raw pointers to cached stat info, URL objects, file-handle storage, and `LocalFileHandler`; the implementation destructor is responsible for cleanup. `pPlugin` is a reference to the owning `File` object's plugin pointer, allowing an open redirect path such as erasure coding to replace the public file plugin.

The main state fields are:

- `pFileState` and `pStatus` for lifecycle and last error.
- `pStatInfo`, `pFileUrl`, `pDataServer`, `pLoadBalancer`, `pStateRedirect`, and `pWrtRecoveryRedir` for URL/stat routing state.
- `pFileHandle`, `pOpenMode`, `pOpenFlags`, and `pSessionId` for server-side stateful identity.
- `pToBeRecovered` and `pInTheFly` for outstanding/recovering requests.
- `pDoRecoverRead`, `pDoRecoverWrite`, `pFollowRedirects`, `pUseVirtRedirector`, `pIsChannelEncrypted`, and `pAllowBundledClose` for behavior toggles.
- Monitoring counters `pOpenTime`, byte counters, operation counters, vector segment counts, and `pCloseReason`.
- `pTemplateFileWp` for template-based open/clone.

The public property API declared here supports `ReadRecovery`, `WriteRecovery`, `FollowRedirects`, `BundledClose`, and selected read-only state queries such as `DataServer`, `LastURL`, and `WrtRecoveryRedir` in the implementation. URL CGI parameters can also disable read/write recovery during open.

## Dependencies and integration points

The header depends on XRootD client response, transport, file-system, message, local-file, optional, and plugin interfaces. It also includes `XrdSysPthread` for locking, `XrdSysPageSize` for page I/O semantics, POSIX `timeval` and `iovec`, and standard containers for request tracking and xattr/clone/page data.

Friend declarations expose internals to the anonymous page-read and open helper handlers in the `.cc` file. The `FileStateHandlerTemplate` type integrates with the public `ExportedFileTemplate` abstraction from the plugin interface, allowing public `File` objects to pass colocated-open or clone source information without exposing `FileStateHandler` directly.

The class is registered with `DefaultEnv::GetForkHandler()` and `DefaultEnv::GetFileTimer()` by the implementation constructors, so this header's `Lock`, `UnLock`, `Tick`, `TimeOutRequests`, and `AfterForkChild` methods are part of broader process-level runtime coordination. It also integrates with `LocalFileHandler` for `file://` URLs and with optional `FilePlugIn` implementations for erasure-coded or protocol-specific backends.

## Risks and edge cases

The API exposes many static functions that mutate shared handler state through a shared pointer reference. This preserves lifetime across async calls, but makes ownership and lock ordering important. Any new method should follow the existing pattern: hold `pMutex` for state checks and message construction, allocate a `StatefulHandler`, process send params, and hand ownership to `SendOrQueue`.

Raw pointer state is extensive. `RequestData` does not use smart pointers, and `pStatInfo`, URL fields, `pFileHandle`, and handlers are manually managed in the implementation. Header changes that alter ownership contracts need corresponding destructor, failure, and recovery-path review.

State-machine invariants are implicit rather than type-enforced. For example, most operations require `Opened` or `Recovering`, close requires no in-flight requests unless bundled close is enabled, and template operations require the source handler to be alive, open, connected, and same-filesystem capable. These constraints are enforced in the `.cc` file but are not encoded in the type system.

Recovery and redirect toggles can be changed through string properties and URL parameters. This is flexible but makes behavior depend on open-time URL parsing and mutable properties; tests should cover combinations of read-only/update modes with disabled recovery.

The header declares `PreRead`, but the public `File::PreRead` path currently does not call it in the non-plugin case in the adjacent wrapper. This means the declared/implemented preread path may be underused or only reachable internally unless the wrapper changes.

## Test signals

Header-level validation should focus on API contract coverage through `XrdCl::File`:

- Compile/link coverage for every declared static operation, especially newer declarations such as page I/O, xattrs, checkpointing, and clone.
- Public property tests for `ReadRecovery`, `WriteRecovery`, `FollowRedirects`, `BundledClose`, and read-only properties populated after open.
- Template export/open/clone tests using `FileStateHandlerTemplate` through `File::GetFileTemplate`, `OpenUsingTemplate`, and `Clone`.
- Fork/timer integration tests that confirm handlers register, lock/unlock, timeout queued recovery requests, and child-side recovery state is selected correctly.
- Negative state tests for operations before open, during open, during recovery, after error, and during close.
