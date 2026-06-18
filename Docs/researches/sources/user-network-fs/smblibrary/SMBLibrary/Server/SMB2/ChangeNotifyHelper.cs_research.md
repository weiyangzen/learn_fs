<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs

## Purpose
SMB2 change-notify handling. It starts asynchronous file-store notification monitoring, returns the interim async response, and later queues a final notify or error response when the callback fires.

## APIs, Types, and Functions
`GetChangeNotifyInterimResponse()` creates the async context and calls `IFileStore.NotifyChange()`. `OnNotifyChangeCompleted()` is the callback that removes the context and enqueues `ChangeNotifyResponse` or `ErrorResponse`.

## Control Flow, State, and Persistence
The helper resolves the session and open file, builds an `SMB2AsyncContext`, locks it to avoid final-before-interim races, and handles `STATUS_PENDING` as async. `STATUS_NOT_SUPPORTED` is deliberately converted to pending to avoid repeated Windows client retries. Completion removes the context and uses session signing state for final responses. State lives in the connection async-context collection and queued SMB responses.

## Dependencies and Integration
Called by SMB2 dispatch after tree/share validation. It depends on `IFileStore.NotifyChange()`, `SMBServer.EnqueueResponse()`, `SMB2AsyncContext`, session open-file tables, and signing metadata.

## Risks and Test Signals
Risks include null `openFile` if an invalid `FileId` reaches the helper, indefinite pending responses for stores that do not support notifications, callback races with cancel, and missing `SessionID` on error responses. Test pending notify, cancel, successful buffer delivery, cleanup/enumeration statuses, invalid file IDs, unsupported stores, and signed sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs -->
