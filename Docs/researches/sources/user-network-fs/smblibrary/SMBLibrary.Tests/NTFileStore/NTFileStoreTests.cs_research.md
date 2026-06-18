<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs

## Purpose
`NTFileStoreTests.cs` defines a reusable abstract MSTest suite for `INTFileStore` implementations, currently focused on notify-change cancellation.

## Important APIs, Types, And Functions
The class stores an `INTFileStore`, a test directory name `Dir`, and nullable `m_notifyChangeStatus`. `TestCancel` calls `CreateFile`, `NotifyChange`, `Cancel`, and `CloseFile`. `OnNotifyChangeCompleted` records callback status. `CreateTestDirectory` opens or creates the test directory.

## Control Flow
The test ensures a directory exists, opens it as a directory, issues a notify request for file name, last write, and directory name changes, asserts `STATUS_PENDING`, sleeps briefly, cancels the request, closes the handle, waits for callback completion, and expects `STATUS_CANCELLED`.

## State And Persistence
The test may create a backing directory named `Dir` in the concrete store. It keeps callback status in memory.

## Dependencies And Integration Points
It depends only on the `INTFileStore` contract and MSTest. `NTDirectoryFileSystemTests` supplies a Win32 concrete store.

## Risks
The busy-wait loops can hang if callback completion never occurs. `m_notifyChangeStatus` is not reset inside `TestCancel`, which matters if test instances are reused. The one-millisecond sleep makes race timing implementation-dependent.

## Test Signals
It provides a focused signal for asynchronous notify cancellation semantics and callback status propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs -->
