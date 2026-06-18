<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs

## Purpose
`ThreadingHelper.cs` exposes minimal kernel32 thread-handle functions needed by Win32 notify cancellation.

## Important APIs, Types, And Functions
The class P/Invokes `GetCurrentThreadId`, `OpenThread`, and `CloseHandle`.

## Control Flow
There is no additional managed control flow; callers directly invoke the native functions. `NTDirectoryFileSystem.NotifyChange` records the worker thread ID, and `Cancel` opens that thread and closes the handle after alerting or cancelling synchronous I/O.

## State And Persistence
No managed state is stored. Native thread handles returned by `OpenThread` must be closed by callers.

## Dependencies And Integration Points
It depends on kernel32 and is tightly coupled to `NTDirectoryFileSystem` notify/cancel behavior.

## Risks
The helper exposes raw handles and access masks, so callers must request correct permissions and always close handles. It is Windows-only and unguarded by platform checks.

## Test Signals
Indirectly exercised by `NTDirectoryFileSystemTests.TestCancel` on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs -->
