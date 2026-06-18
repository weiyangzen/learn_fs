<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs

## Purpose
SMB2 cancel handling for asynchronous operations. It locates an async context by `AsyncID`, asks the backing file store to cancel the captured I/O request, and returns the required async `STATUS_CANCELLED` error response only when cancellation is accepted.

## APIs, Types, and Functions
`CancelHelper.GetCancelResponse(CancelRequest, SMB2ConnectionState)` is the only entry point. It uses `SMB2AsyncContext`, `SMB2Session`, `OpenFileObject`, `ISMBShare.FileStore.Cancel()`, and `ErrorResponse`.

## Control Flow, State, and Persistence
Only async-header cancel requests are processed. The helper resolves the async context, tree, and open file, calls `Cancel()`, removes the async context on success, `STATUS_CANCELLED`, or `STATUS_NOT_SUPPORTED`, then returns an async-header error response for the target request. Missing contexts, non-async cancel requests, or failed cancels produce no response. State is the in-memory async-context table.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` for async cancel requests and for regular cancel commands after tree lookup. It assumes async contexts were created by helpers such as change notify.

## Risks and Test Signals
Risks include null-session assumptions, no response on failed cancel causing client request-expiration behavior, and treating `STATUS_NOT_SUPPORTED` as a successful cleanup path to support change notify behavior. Test async change-notify cancellation, unknown `AsyncID`, non-async cancel, backing-store cancel failures, and async context removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs -->
