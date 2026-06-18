<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs

## Purpose
`PendingRequestCollection.cs` tracks outstanding notify-change requests by file handle for `NTDirectoryFileSystem`.

## Important APIs, Types, And Functions
The internal class owns `Dictionary<IntPtr, List<PendingRequest>> m_handleToNotifyChangeRequests`. It provides `Add(PendingRequest request)`, `Remove(IntPtr handle, uint threadID)`, and `GetRequestsByHandle(IntPtr handle)`.

## Control Flow
`Add` locks the dictionary, appends to an existing per-handle list or creates a new list. `Remove` locks, scans the per-handle list for matching thread IDs, removes all matches, and removes the handle key when the list becomes empty. `GetRequestsByHandle` returns a copy of the current list or an empty list.

## State And Persistence
State is in-memory only and lasts for the `NTDirectoryFileSystem` instance. It represents active notify worker threads and is not persisted.

## Dependencies And Integration Points
It depends on `PendingRequest` from `NTDirectoryFileSystem.cs`. `CloseFile`, `NotifyChange`, and `Cancel` use it to find and cancel pending notifications.

## Risks
`GetRequestsByHandle` reads the dictionary without taking the same lock used by `Add`/`Remove`, so concurrent access can race. Removal by thread ID assumes uniqueness per handle. Callers can receive copied lists containing request objects that are concurrently completed or removed.

## Test Signals
No direct unit tests. It is exercised indirectly by `NTFileStoreTests.TestCancel` through notify/cancel behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs -->
