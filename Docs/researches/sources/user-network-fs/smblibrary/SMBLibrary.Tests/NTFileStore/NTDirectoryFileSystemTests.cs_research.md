<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs

## Purpose
`NTDirectoryFileSystemTests.cs` binds the generic `NTFileStoreTests` suite to the Win32 `NTDirectoryFileSystem` implementation rooted at `C:\Tests`.

## Important APIs, Types, And Functions
The class derives from `NTFileStoreTests`, creates `NTDirectoryFileSystem(TestDirectoryPath)`, ensures the test directory exists in a static constructor, and overrides `TestCancel`.

## Control Flow
Construction passes a real Win32 filesystem-backed store to the abstract base test. The overridden cancel test marks itself inconclusive on non-Windows platforms, otherwise delegates to the base `TestCancel`.

## State And Persistence
It creates or reuses the persistent local directory `C:\Tests` on Windows. The inherited test creates a child directory named `Dir`.

## Dependencies And Integration Points
It depends on Windows, `SMBLibrary.Win32.NTDirectoryFileSystem`, `System.Runtime.InteropServices.RuntimeInformation`, and the base `INTFileStore` notify/cancel test. It is the primary test in this subset for Win32 change-notify cancellation.

## Risks
The hard-coded `C:\Tests` path requires permissions and leaves artifacts. Non-Windows environments skip the actual behavior. The class only covers cancel behavior, not the broader Win32 file-store API.

## Test Signals
On Windows, it validates that a pending notify request can be cancelled and completes with `STATUS_CANCELLED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs -->
