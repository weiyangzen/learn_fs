<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs

## Purpose
`NTFileSystemAdapter.Set.cs` implements selected file information updates for the managed adapter: basic metadata, rename, disposition/delete, allocation size, and EOF size.

## Important APIs, Types, And Functions
The public method is `SetFileInformation(object handle, FileInformation information)`. It handles `FileBasicInformation`, `FileRenameInformationType2`, `FileDispositionInformation`, `FileAllocationInformation`, and `FileEndOfFileInformation`. The private helper `IsFileExists(string path)` probes the backing filesystem for replacement decisions.

## Control Flow
For basic information it extracts hidden/read-only/archive flags, calls `m_fileSystem.SetAttributes`, then sets creation, last-write, and last-access timestamps. For rename it normalizes the target to a leading backslash, closes an open stream, optionally deletes an existing target when `ReplaceIfExists` is true, moves the backing object, and updates `fileHandle.Path`. For disposition it closes the stream and deletes immediately when `DeletePending` is true. Allocation and EOF requests both call `fileHandle.Stream.SetLength`.

## State And Persistence
This file mutates backing filesystem metadata and file contents. Rename updates handle state to the new path. Disposition deletes immediately rather than deferring strictly to handle close. Allocation/EOF truncate or extend the underlying stream.

## Dependencies And Integration Points
It depends on `m_fileSystem` mutation APIs, core adapter logging and exception mapping, and SMBLibrary file-information classes. It participates in SMB set-info handling through `INTFileStore.SetFileInformation`.

## Risks
`FileDispositionInformation` deletes immediately, which differs from full NT delete-pending semantics and can expose timing differences. Rename closes the stream and does not reopen it, so subsequent reads/writes through the same handle may fail. Allocation/EOF assume `fileHandle.Stream` is non-null; directory or metadata-only handles can throw. `FileBasicInformation` ignores the NT convention that zero timestamps mean unchanged. Replacement deletion does not distinguish files from non-empty directories beyond backing errors.

## Test Signals
No direct adapter set-info tests are present. Tests should cover rename case-only changes, replace/no-replace collision status, delete-on-close semantics, stream availability after rename, timestamp zero handling, and directory set-info behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs -->
