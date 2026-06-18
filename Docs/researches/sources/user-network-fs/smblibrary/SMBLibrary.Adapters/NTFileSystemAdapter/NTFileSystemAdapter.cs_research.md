<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs

## Purpose
`NTFileSystemAdapter.cs` is the core of the managed `IFileSystem` to `INTFileStore` adapter. It implements SMB-style create/open, read, write, close, flush, basic unsupported operations, logging, exception mapping, create-option mapping, and allocation-size rounding.

## Important APIs, Types, And Functions
The class `NTFileSystemAdapter : INTFileStore` owns `m_fileSystem`, exposes `LogEntryAdded`, and implements `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `FlushFileBuffers`, `LockFile`, `UnlockFile`, security-info stubs, notify/cancel stubs, `DeviceIOControl`, `Log`, `ToNTStatus`, `ToFileOptions`, `ToFileOptionsString`, and `GetAllocationSize`. `OpenFileStream` adapts SMB desired access/share/create options to .NET stream open calls.

## Control Flow
`CreateFile` derives create access and directory/file constraints from SMB inputs, rejects named streams when unsupported, probes the entry, then branches by `CreateDisposition`. It opens existing objects, creates new files or directories, truncates for overwrite, or deletes and recreates for supersede. If file data access is requested and the target is not a directory, it opens a stream with mapped share and option flags. `ReadFile` seeks, reads, and trims EOF responses; `WriteFile` seeks and writes all bytes. `CloseFile` closes the stream and performs manual delete-on-close when no stream was opened.

## State And Persistence
The adapter stores only the backing filesystem reference and log subscribers. File state lives in returned `FileHandle` objects, including path, directory flag, stream, and delete-on-close flag. Create, overwrite, supersede, write, and close/delete operations mutate the backing filesystem.

## Dependencies And Integration Points
It depends on `DiskAccessLibrary.FileSystems.Abstractions.IFileSystem`, SMBLibrary `INTFileStore`, `NTFileStoreHelper`, `FileHandle`, `NTStatus`, and `Utilities.LogEntry`. Partial class files implement query and set operations. It is suitable for non-Win32 backends that expose the `IFileSystem` abstraction.

## Risks
The implementation is intentionally incomplete for locks, security descriptors, notify change, cancellation, and FSCTLs. NT create disposition semantics are approximated; supersede deletes before recreate and may lose metadata. Named-stream detection rejects any colon in the path when streams are unsupported, which may also reject unusual path syntaxes. Exception-to-status mapping is coarse and returns `STATUS_DATA_ERROR` for many I/O failures. Delete-on-close relies on .NET `FileOptions.DeleteOnClose` when a stream exists but manual deletion for directories or metadata-only opens.

## Test Signals
This subset does not include direct tests for the managed adapter. Indirect expectations are implied by `INTFileStore` tests and SMB server file operations, but notify/cancel tests target the Win32 implementation, not this adapter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs -->
